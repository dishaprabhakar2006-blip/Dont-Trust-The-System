from fastapi.testclient import TestClient

from backend.app import main
from backend.app.repository import InMemoryTeamRepository


def _client(monkeypatch):
    monkeypatch.setattr(main, "repository", InMemoryTeamRepository())
    return TestClient(main.app)


def _team(client, name, p1, p2):
    team = client.post(
        "/teams", json={"player_name": p1, "team_name": name}
    ).json()
    client.post(
        "/teams/join",
        json={"player_name": p2, "join_code": team["join_code"]},
    )
    return team


def test_team_name_defaults_when_missing(monkeypatch):
    client = _client(monkeypatch)
    data = client.post("/teams", json={"player_name": "Disha"}).json()
    assert data["team_name"] == "Disha's team"


def test_leaderboard_ranks_by_score_and_hides_private_fields(monkeypatch):
    client = _client(monkeypatch)
    alpha = _team(client, "Alpha", "a1", "a2")
    _team(client, "Beta", "b1", "b2")

    analyst_id = alpha["players"][0]["player_id"]
    response = client.post(
        f"/teams/{alpha['team_id']}/actions",
        json={"player_id": analyst_id, "answer": "hydra"},
    )
    assert response.status_code == 200

    rows = client.get("/leaderboard").json()
    assert [row["team_name"] for row in rows] == ["Alpha", "Beta"]
    assert [row["rank"] for row in rows] == [1, 2]
    assert rows[0]["score"] == 5
    for row in rows:
        assert set(row) == {
            "rank",
            "team_name",
            "score",
            "current_stage",
            "game_status",
            "time_taken_seconds",
        }