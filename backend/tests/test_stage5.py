from datetime import timedelta

from fastapi.testclient import TestClient

from backend.app import main
from backend.app.repository import InMemoryTeamRepository


def _team5(monkeypatch):
    monkeypatch.setattr(main, "repository", InMemoryTeamRepository())
    monkeypatch.setattr(main, "START_STAGE", 5)
    client = TestClient(main.app)
    t = client.post("/teams", json={"player_name": "a", "team_name": "T5"}).json()
    j = client.post("/teams/join", json={"player_name": "m", "join_code": t["join_code"]}).json()
    ids = {p["role"]: p["player_id"] for p in j["players"]}
    client.get(f"/teams/{t['team_id']}/state")  # starts the countdown
    return client, t["team_id"], ids


def _ans(client, tid, pid, qid, answer):
    return client.post(
        f"/teams/{tid}/actions",
        json={"player_id": pid, "question_id": qid, "answer": answer},
    )


def _play(client, tid, ids, analyst_name, monitor_name):
    a, m = ids["Analyst"], ids["Monitor"]
    assert _ans(client, tid, a, "a1", "svc_backup01").status_code == 200
    assert _ans(client, tid, a, "a2", "archiveindex").status_code == 200
    assert _ans(client, tid, a, "a3", analyst_name).status_code == 200
    assert _ans(client, tid, m, "m1", "n8443").status_code == 200
    assert _ans(client, tid, m, "m2", monitor_name).status_code == 200
    return client.get(f"/teams/{tid}/state").json()


def test_stage5_full_win_scores_forty(monkeypatch):
    client, tid, ids = _team5(monkeypatch)
    state = _play(client, tid, ids, "jordan.lee", "jordan.lee")
    assert state["game_status"] == "completed"
    assert state["outcome"] == "full"
    assert state["score"] == 40


def test_stage5_wrong_insider_gets_half_points_not_a_penalty(monkeypatch):
    client, tid, ids = _team5(monkeypatch)
    state = _play(client, tid, ids, "avery.park", "priya.nair")
    assert state["outcome"] == "partial"
    assert state["score"] == 7 + 7 + 3 + 10 + 5


def test_stage5_timeout_means_data_lost_and_small_penalty(monkeypatch):
    client, tid, ids = _team5(monkeypatch)
    assert _ans(client, tid, ids["Monitor"], "m1", "n8443").status_code == 200
    real_now = main.utc_now()
    monkeypatch.setattr(main, "utc_now", lambda: real_now + timedelta(minutes=10))
    state = client.get(f"/teams/{tid}/state").json()
    assert state["game_status"] == "completed"
    assert state["outcome"] == "data_lost"
    assert state["score"] == 5  # 10 earned, minus 5
    late = _ans(client, tid, ids["Analyst"], "a1", "svc_backup01")
    assert late.status_code == 409