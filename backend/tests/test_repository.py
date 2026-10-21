from datetime import datetime, timezone
from threading import Lock, Thread
from types import ModuleType
import sys

from backend.app.main import Player, Team
from backend.app.repository import (
    FirebaseTeamRepository,
    InMemoryTeamRepository,
    create_repository_from_env,
)


class FakeReference:
    def __init__(self, database, path: str) -> None:
        self.database = database
        self.path = path

    def get(self):
        with self.database.lock:
            return self.database.values.get(self.path)

    def set(self, value):
        with self.database.lock:
            self.database.values[self.path] = value

    def transaction(self, updater):
        with self.database.lock:
            value = updater(self.database.values.get(self.path))
            self.database.values[self.path] = value
            return value


class FakeDatabase:
    def __init__(self) -> None:
        self.values = {}
        self.lock = Lock()

    def reference(self, path: str, app=None):
        return FakeReference(self, path)


def sample_team() -> Team:
    now = datetime.now(timezone.utc)
    return Team(
        team_id="team-1",
        join_code="ABC234",
        players=[Player(player_id="player-1", player_name="Alex", role="Analyst")],
        created_at=now,
        updated_at=now,
    )


def test_repository_defaults_to_memory_without_firebase_config(monkeypatch) -> None:
    monkeypatch.delenv("FIREBASE_DATABASE_URL", raising=False)

    assert isinstance(create_repository_from_env(), InMemoryTeamRepository)


def test_repository_selects_firebase_when_database_configured(monkeypatch) -> None:
    admin = ModuleType("firebase_admin")
    admin.initialize_app = lambda *args, **kwargs: "fake-app"
    credentials = ModuleType("firebase_admin.credentials")
    credentials.ApplicationDefault = lambda: "fake-credential"
    db = ModuleType("firebase_admin.db")
    admin.credentials = credentials
    admin.db = db
    monkeypatch.setitem(sys.modules, "firebase_admin", admin)
    monkeypatch.setitem(sys.modules, "firebase_admin.credentials", credentials)
    monkeypatch.setitem(sys.modules, "firebase_admin.db", db)
    monkeypatch.setenv("FIREBASE_DATABASE_URL", "https://example.invalid")
    monkeypatch.delenv("FIREBASE_SERVICE_ACCOUNT_PATH", raising=False)
    monkeypatch.delenv("FIREBASE_DATABASE_EMULATOR_HOST", raising=False)

    assert isinstance(create_repository_from_env(), FirebaseTeamRepository)


def test_memory_repository_persists_and_atomically_updates_shared_team() -> None:
    repository = InMemoryTeamRepository()
    team = sample_team()
    assert repository.create(team)

    def add_completion(current: Team) -> None:
        current.completed_actions.append("stage-1:analyst")
        current.current_stage = 2

    updated = repository.update(team.team_id, add_completion)
    loaded_by_code = repository.get_by_join_code(team.join_code)

    assert updated.current_stage == 2
    assert loaded_by_code.completed_actions == ["stage-1:analyst"]
    # Reads return copies, so an unsaved mutation cannot alter shared state.
    loaded_by_code.score = 99
    assert repository.get(team.team_id).score == 0


def test_firebase_adapter_persists_team_and_serializes_concurrent_updates() -> None:
    database = FakeDatabase()
    repository = FirebaseTeamRepository(database)
    team = sample_team()
    assert repository.create(team)
    assert repository.get_by_join_code(team.join_code).team_id == team.team_id

    def increment(_: int) -> None:
        def add_point(current: Team) -> None:
            current.score += 1

        repository.update(team.team_id, add_point)

    workers = [Thread(target=increment, args=(index,)) for index in range(12)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()

    assert repository.get(team.team_id).score == 12


def test_gitignore_excludes_environment_and_firebase_credential_files() -> None:
    with open(".gitignore", encoding="utf-8") as ignore_file:
        contents = ignore_file.read()

    for entry in [".venv/", ".env", "*-firebase-adminsdk-*.json", "service-account*.json"]:
        assert entry in contents
