"""Team persistence adapters and environment-based repository selection."""

from __future__ import annotations

from copy import deepcopy
from threading import RLock
from typing import Any, Callable, Protocol

from backend.app.models import Team


TeamUpdater = Callable[[Team], None]


class TeamRepository(Protocol):
    def get(self, team_id: str) -> Team | None: ...

    def get_by_join_code(self, join_code: str) -> Team | None: ...

    def create(self, team: Team) -> bool: ...

    def save(self, team: Team) -> None: ...

    def update(self, team_id: str, updater: TeamUpdater) -> Team | None: ...

    def list_all(self) -> list[Team]: ...

class InMemoryTeamRepository:
    """Thread-safe local store that returns copies to prevent unsafe mutation."""

    def __init__(self) -> None:
        self._teams: dict[str, Any] = {}
        self._team_ids_by_code: dict[str, str] = {}
        self._lock = RLock()

    def get(self, team_id: str) -> Team | None:
        with self._lock:
            team = self._teams.get(team_id)
            return deepcopy(team) if team is not None else None

    def get_by_join_code(self, join_code: str) -> Team | None:
        with self._lock:
            team_id = self._team_ids_by_code.get(join_code)
            team = self._teams.get(team_id) if team_id else None
            return deepcopy(team) if team is not None else None

    def create(self, team: Team) -> bool:
        with self._lock:
            if team.join_code in self._team_ids_by_code:
                return False
            self._teams[team.team_id] = deepcopy(team)
            self._team_ids_by_code[team.join_code] = team.team_id
            return True

    def save(self, team: Team) -> None:
        with self._lock:
            self._teams[team.team_id] = deepcopy(team)
            self._team_ids_by_code[team.join_code] = team.team_id

    def update(self, team_id: str, updater: TeamUpdater) -> Team | None:
        with self._lock:
            existing = self._teams.get(team_id)
            if existing is None:
                return None
            updated = deepcopy(existing)
            updater(updated)
            self._teams[team_id] = deepcopy(updated)
            return deepcopy(updated)

    def list_all(self) -> list[Team]:
        with self._lock:
            return [deepcopy(team) for team in self._teams.values()]


class FirebaseTeamRepository:
    """Firebase Realtime Database adapter.

    Team mutations use Realtime Database transactions, making role assignment
    and mission completion atomic across API workers and devices.
    """

    def __init__(self, database: Any, firebase_app: Any = None) -> None:
        self._database = database
        self._firebase_app = firebase_app

    def _ref(self, path: str) -> Any:
        return self._database.reference(path, app=self._firebase_app)

    @staticmethod
    def _to_model(value: Any) -> Team | None:
        if value is None:
            return None
        return Team.model_validate(value)

    @staticmethod
    def _to_dict(team: Team) -> dict[str, Any]:
        return team.model_dump(mode="json")

    def get(self, team_id: str) -> Team | None:
        return self._to_model(self._ref(f"teams/{team_id}").get())

    def get_by_join_code(self, join_code: str) -> Team | None:
        team_id = self._ref(f"join_codes/{join_code}").get()
        return self.get(team_id) if team_id else None

    def create(self, team: Team) -> bool:
        code_ref = self._ref(f"join_codes/{team.join_code}")
        result = code_ref.transaction(
            lambda current: current if current is not None else team.team_id
        )
        if result != team.team_id:
            return False
        self._ref(f"teams/{team.team_id}").set(self._to_dict(team))
        return True

    def save(self, team: Team) -> None:
        self._ref(f"teams/{team.team_id}").set(self._to_dict(team))

    def update(self, team_id: str, updater: TeamUpdater) -> Team | None:
        ref = self._ref(f"teams/{team_id}")
        result = ref.transaction(
            lambda current: self._update_value(current, updater)
        )
        return self._to_model(result)

    @classmethod
    def _update_value(cls, current: Any, updater: TeamUpdater) -> Any:
        team = cls._to_model(current)
        if team is None:
            return current
        updater(team)
        return cls._to_dict(team)


def create_repository_from_env() -> TeamRepository:
    """Select Firebase when configured; otherwise use the local memory store."""
    import os
    from dotenv import load_dotenv

    load_dotenv()
    database_url = os.getenv("FIREBASE_DATABASE_URL", "").strip()
    if not database_url:
        return InMemoryTeamRepository()

    try:
        import firebase_admin
        from firebase_admin import credentials, db
    except ImportError as exc:
        raise RuntimeError(
            "Firebase is configured but firebase-admin is missing. "
            "Install project requirements."
        ) from exc

    options = {"databaseURL": database_url}
    service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "").strip()
    emulator_host = os.getenv("FIREBASE_DATABASE_EMULATOR_HOST", "").strip()
    if emulator_host:
        os.environ["FIREBASE_DATABASE_EMULATOR_HOST"] = emulator_host
        firebase_app = firebase_admin.initialize_app(options=options)
    elif service_account_path:
        credential = credentials.Certificate(service_account_path)
        firebase_app = firebase_admin.initialize_app(credential, options)
    else:
        # Uses GOOGLE_APPLICATION_CREDENTIALS or the platform's Application
        # Default Credentials (for example, an attached service identity).
        firebase_app = firebase_admin.initialize_app(
            credentials.ApplicationDefault(), options
        )
    return FirebaseTeamRepository(db, firebase_app)

def list_all(self) -> list[Team]:
    value = self._ref("teams").get() or {}
    teams = []
    for item in value.values():
        team = self._to_model(item)
        if team is not None:
            teams.append(team)
    return teams
