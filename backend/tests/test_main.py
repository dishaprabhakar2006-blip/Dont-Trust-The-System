from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI

from backend.app import main
from backend.app.main import app, configure_cors, parse_frontend_origins
from backend.app.missions import MISSIONS
from backend.app.repository import InMemoryTeamRepository

client = TestClient(app)

PASSWORD = "novadb02_4471_1410"


def test_health_endpoint_returns_healthy_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_and_join_team_assigns_distinct_roles() -> None:
    created = client.post("/teams", json={"player_name": "Alex"})

    assert created.status_code == 201
    team = created.json()
    assert len(team["join_code"]) == 6
    assert team["players"][0]["role"] == "Analyst"

    joined = client.post("/teams/join", json={
        "player_name": "Sam", "join_code": team["join_code"].lower()
    })

    assert joined.status_code == 200
    joined_team = joined.json()
    assert joined_team["team_id"] == team["team_id"]
    assert [player["role"] for player in joined_team["players"]] == ["Analyst", "Monitor"]


def test_join_rejects_unknown_code() -> None:
    response = client.post("/teams/join", json={
        "player_name": "Sam", "join_code": "NOPE42"
    })

    assert response.status_code == 404


def test_join_rejects_team_that_already_has_both_roles() -> None:
    created = client.post("/teams", json={"player_name": "Alex"}).json()
    client.post("/teams/join", json={
        "player_name": "Sam", "join_code": created["join_code"]
    })

    response = client.post("/teams/join", json={
        "player_name": "Taylor", "join_code": created["join_code"]
    })

    assert response.status_code == 409


def test_state_contains_shared_team_fields_and_role_assignments() -> None:
    created = client.post("/teams", json={"player_name": "Alex"}).json()
    client.post("/teams/join", json={
        "player_name": "Sam", "join_code": created["join_code"]
    })

    response = client.get(f"/teams/{created['team_id']}/state")

    assert response.status_code == 200
    state = response.json()
    assert state["team_id"] == created["team_id"]
    assert state["join_code"] == created["join_code"]
    assert [player["role"] for player in state["players"]] == ["Analyst", "Monitor"]
    assert state["current_stage"] == 1
    assert state["game_status"] == "in_progress"
    assert state["started_at"]
    assert state["remaining_seconds"] is not None
    assert state["score"] == 0
    assert state["completed_actions"] == []
    assert state["created_at"]
    assert state["updated_at"] >= state["created_at"]
    assert "answers" not in state


def test_team_states_are_isolated() -> None:
    first = client.post("/teams", json={"player_name": "Alex"}).json()
    second = client.post("/teams", json={"player_name": "Jordan"}).json()

    first_state = client.get(f"/teams/{first['team_id']}/state").json()
    second_state = client.get(f"/teams/{second['team_id']}/state").json()

    assert first_state["team_id"] != second_state["team_id"]
    assert first_state["join_code"] != second_state["join_code"]
    assert [p["player_name"] for p in first_state["players"]] == ["Alex"]
    assert [p["player_name"] for p in second_state["players"]] == ["Jordan"]


def test_state_rejects_unknown_team_id() -> None:
    response = client.get("/teams/not-a-team/state")

    assert response.status_code == 404


def create_full_team() -> dict:
    team = client.post("/teams", json={"player_name": "Alex"}).json()
    joined = client.post("/teams/join", json={
        "player_name": "Sam", "join_code": team["join_code"]
    }).json()
    team["players"] = joined["players"]
    return team


def test_mission_retrieval_is_role_specific_and_does_not_leak_answers() -> None:
    team = create_full_team()

    analyst = client.get(
        f"/teams/{team['team_id']}/mission",
        params={"player_id": team["players"][0]["player_id"]}
    )
    monitor = client.get(
        f"/teams/{team['team_id']}/mission",
        params={"player_id": team["players"][1]["player_id"]}
    )

    assert analyst.status_code == monitor.status_code == 200
    assert analyst.json()["role"] == "Analyst"
    assert monitor.json()["role"] == "Monitor"
    for mission in [analyst.json(), monitor.json()]:
        serialized = str(mission).lower()
        assert "answer_key" not in serialized
        assert "'answers'" not in serialized
        assert "'hint'" not in serialized
        assert PASSWORD not in serialized
        assert "ks-a7f3" not in serialized
        assert "203.0.113.77" not in serialized  # hidden until login
    # Locked questions are not even listed before login.
    assert [q["id"] for q in analyst.json()["questions"]] == ["a1"]
    assert [q["id"] for q in monitor.json()["questions"]] == ["m1"]


def test_mission_rejects_player_not_assigned_to_team() -> None:
    team = create_full_team()

    response = client.get(
        f"/teams/{team['team_id']}/mission",
        params={"player_id": "someone-else"}
    )

    assert response.status_code == 403


def test_incorrect_answer_is_rejected_without_progress() -> None:
    team = create_full_team()

    response = client.post(f"/teams/{team['team_id']}/actions", json={
        "player_id": team["players"][0]["player_id"],
        "question_id": "a1",
        "answer": "not the answer"
    })

    assert response.status_code == 400
    state = client.get(f"/teams/{team['team_id']}/state").json()
    assert state["current_stage"] == 1
    assert state["score"] == 0
    assert state["completed_actions"] == []


def test_both_roles_must_submit_correct_answer_to_unlock_next_stage() -> None:
    team = create_full_team()
    analyst_id = team["players"][0]["player_id"]
    monitor_id = team["players"][1]["player_id"]
    url = f"/teams/{team['team_id']}/actions"

    a1 = client.post(url, json={
        "player_id": analyst_id, "question_id": "a1", "answer": PASSWORD.upper()
    })
    assert a1.status_code == 200
    assert a1.json()["stage_completed"] is False

    m1 = client.post(url, json={
        "player_id": monitor_id, "question_id": "m1", "answer": PASSWORD
    })
    assert m1.status_code == 200
    assert m1.json()["stage_completed"] is False
    assert m1.json()["current_stage"] == 1

    a2 = client.post(url, json={
        "player_id": analyst_id, "question_id": "a2", "answer": "KS-A7F3"
    })
    assert a2.status_code == 200
    assert a2.json()["stage_completed"] is False

    m2 = client.post(url, json={
        "player_id": monitor_id, "question_id": "m2", "answer": "203.0.113.77"
    })
    assert m2.status_code == 200
    assert m2.json()["stage_completed"] is True
    assert m2.json()["current_stage"] == 2

    next_mission = client.get(
        f"/teams/{team['team_id']}/mission",
        params={"player_id": analyst_id}
    )
    assert next_mission.json()["stage"] == 2


def test_duplicate_submission_cannot_complete_or_score_twice() -> None:
    team = create_full_team()
    player_id = team["players"][0]["player_id"]
    endpoint = f"/teams/{team['team_id']}/actions"
    body = {"player_id": player_id, "question_id": "a1", "answer": PASSWORD}

    first = client.post(endpoint, json=body)
    duplicate = client.post(endpoint, json=body)

    assert first.status_code == 200
    assert duplicate.status_code == 409
    state = client.get(f"/teams/{team['team_id']}/state").json()
    assert state["score"] == 2


def test_correct_answers_award_points_once_and_unlock_stage() -> None:
    team = create_full_team()
    analyst_id, monitor_id = [player["player_id"] for player in team["players"]]
    endpoint = f"/teams/{team['team_id']}/actions"

    a1 = client.post(endpoint, json={
        "player_id": analyst_id, "question_id": "a1", "answer": PASSWORD})
    m1 = client.post(endpoint, json={
        "player_id": monitor_id, "question_id": "m1", "answer": PASSWORD})
    assert a1.json()["points_awarded"] == 2
    assert m1.json()["points_awarded"] == 2

    a2 = client.post(endpoint, json={
        "player_id": analyst_id, "question_id": "a2", "answer": "ks-a7f3"})
    m2 = client.post(endpoint, json={
        "player_id": monitor_id, "question_id": "m2", "answer": "203.0.113.77"})
    assert a2.json()["points_awarded"] == 3
    assert m2.json()["points_awarded"] == 3
    assert m2.json()["score"] == 10
    assert m2.json()["completed_stages"] == [1]
    assert m2.json()["current_stage"] == 2


def test_timer_expiry_prevents_scoring_and_progress(monkeypatch) -> None:
    current = datetime(2026, 1, 1, tzinfo=timezone.utc)
    monkeypatch.setattr(main, "utc_now", lambda: current)
    monkeypatch.setattr(main, "GAME_DURATION_SECONDS", 30)
    team = create_full_team()
    player_id = team["players"][0]["player_id"]
    started = client.get(f"/teams/{team['team_id']}/state").json()
    assert started["remaining_seconds"] == 30

    current += timedelta(seconds=31)
    state = client.get(f"/teams/{team['team_id']}/state").json()
    submission = client.post(f"/teams/{team['team_id']}/actions", json={
        "player_id": player_id, "question_id": "a1", "answer": PASSWORD
    })

    assert state["game_status"] == "expired"
    assert state["remaining_seconds"] == 0
    assert submission.status_code == 409
    final_state = client.get(f"/teams/{team['team_id']}/state").json()
    assert final_state["score"] == 0
    assert final_state["completed_actions"] == []


def test_all_five_stages_produce_final_results_and_reject_more_actions() -> None:
    team = create_full_team()
    players = {player["role"]: player["player_id"] for player in team["players"]}
    action_url = f"/teams/{team['team_id']}/actions"

    for stage in range(1, 6):
        for role in ("Analyst", "Monitor"):
            for q in MISSIONS[stage]["roles"][role]["questions"]:
                response = client.post(action_url, json={
                    "player_id": players[role],
                    "question_id": q["id"],
                    "answer": q["answers"][0],
                })
                assert response.status_code == 200

    result = client.get(f"/teams/{team['team_id']}/results")
    assert result.status_code == 200
    assert result.json()["final"] is True
    assert result.json()["game_status"] == "completed"
    assert result.json()["score"] == 100
    assert result.json()["completed_stages"] == [1, 2, 3, 4, 5]

    rejected = client.post(action_url, json={
        "player_id": players["Analyst"], "question_id": "q1", "answer": "jordan.lee"
    })
    assert rejected.status_code == 409


def test_timer_values_are_shared_and_use_persisted_duration(monkeypatch) -> None:
    now = datetime(2026, 2, 1, tzinfo=timezone.utc)
    monkeypatch.setattr(main, "utc_now", lambda: now)
    monkeypatch.setattr(main, "GAME_DURATION_SECONDS", 90)
    team = create_full_team()

    first_view = client.get(f"/teams/{team['team_id']}/state").json()
    second_view = client.get(f"/teams/{team['team_id']}/state").json()

    assert first_view["started_at"] == second_view["started_at"]
    assert first_view["remaining_seconds"] == second_view["remaining_seconds"] == 90
    assert first_view["duration_seconds"] == 90


def test_concurrent_role_submissions_score_and_unlock_once(monkeypatch) -> None:
    monkeypatch.setattr(main, "repository", InMemoryTeamRepository())
    team = create_full_team()
    url = f"/teams/{team['team_id']}/actions"
    jobs = [
        (team["players"][0]["player_id"], "a1"),
        (team["players"][1]["player_id"], "m1"),
    ]

    def submit(job):
        player_id, question_id = job
        return client.post(url, json={
            "player_id": player_id,
            "question_id": question_id,
            "answer": PASSWORD,
        })

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(submit, jobs))

    assert [response.status_code for response in responses] == [200, 200]
    state = client.get(f"/teams/{team['team_id']}/state").json()
    assert state["score"] == 4
    assert state["completed_stages"] == []
    assert state["current_stage"] == 1


def test_client_cannot_inject_score_or_stage_and_invalid_action_is_rejected() -> None:
    team = create_full_team()
    response = client.post(f"/teams/{team['team_id']}/actions", json={
        "player_id": team["players"][0]["player_id"],
        "question_id": "a1",
        "answer": "incorrect",
        "score": 999999,
        "stage": 5,
    })

    assert response.status_code == 400
    state = client.get(f"/teams/{team['team_id']}/state").json()
    assert state["score"] == 0
    assert state["current_stage"] == 1


def test_localhost_cors_preflight_is_allowed_without_credentials() -> None:
    response = client.options("/health", headers={
        "Origin": "http://localhost:43210",
        "Access-Control-Request-Method": "GET",
    })

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:43210"
    assert "access-control-allow-credentials" not in response.headers


def test_configured_frontend_origins_support_comma_separated_values(monkeypatch) -> None:
    monkeypatch.setenv(
        "FRONTEND_ORIGINS",
        " http://192.168.1.20:9001, https://demo.example.test ",
    )
    configured_origins = parse_frontend_origins()
    probe_app = FastAPI()
    configure_cors(probe_app, configured_origins)
    probe_client = TestClient(probe_app)

    response = probe_client.options("/health", headers={
        "Origin": "http://192.168.1.20:9001",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    })
    rejected = probe_client.options("/health", headers={
        "Origin": "http://192.168.1.21:9001",
        "Access-Control-Request-Method": "POST",
    })

    assert configured_origins == [
        "http://192.168.1.20:9001", "https://demo.example.test"
    ]
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://192.168.1.20:9001"
    assert rejected.status_code == 400


def test_cors_rejects_unrestricted_wildcard_origin() -> None:
    try:
        parse_frontend_origins("*")
    except ValueError as exc:
        assert "specific origins" in str(exc)
    else:
        raise AssertionError("Wildcard CORS origin should be rejected")


def test_action_cannot_claim_another_teams_player() -> None:
    first = create_full_team()
    second = create_full_team()

    response = client.post(f"/teams/{first['team_id']}/actions", json={
        "player_id": second["players"][0]["player_id"],
        "question_id": "a1",
        "answer": PASSWORD,
    })

    assert response.status_code == 403


# ---------------- New tests: lockout, locked questions, hints ----------------

def test_five_wrong_answers_lock_the_question() -> None:
    team = create_full_team()
    player_id = team["players"][0]["player_id"]
    url = f"/teams/{team['team_id']}/actions"
    wrong = {"player_id": player_id, "question_id": "a1", "answer": "nope"}

    for _ in range(4):
        assert client.post(url, json=wrong).status_code == 400

    fifth = client.post(url, json=wrong)
    assert fifth.status_code == 400
    assert "Locked" in fifth.json()["detail"]

    # Even the correct answer is refused while the question is locked.
    locked = client.post(url, json={
        "player_id": player_id, "question_id": "a1", "answer": PASSWORD
    })
    assert locked.status_code == 429


def test_locked_question_cannot_be_answered_before_login() -> None:
    team = create_full_team()

    response = client.post(f"/teams/{team['team_id']}/actions", json={
        "player_id": team["players"][0]["player_id"],
        "question_id": "a2",
        "answer": "ks-a7f3",
    })

    assert response.status_code == 404


def test_hint_costs_one_point_once() -> None:
    team = create_full_team()
    player_id = team["players"][0]["player_id"]
    client.post(f"/teams/{team['team_id']}/actions", json={
        "player_id": player_id, "question_id": "a1", "answer": PASSWORD
    })  # score 2, unlocks a2

    hint_url = f"/teams/{team['team_id']}/hint"
    body = {"player_id": player_id, "question_id": "a2"}

    first = client.post(hint_url, json=body)
    second = client.post(hint_url, json=body)

    assert first.status_code == 200
    assert first.json()["hint"]
    assert first.json()["score"] == 1
    assert second.json()["score"] == 1  # asking again is free