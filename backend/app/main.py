
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import math
import os
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from backend.app.repository import TeamRepository, create_repository_from_env
from backend.app.missions import MISSIONS, public_mission
from backend.app.models import Player, Team


# --------------------------------------------------
# Request models
# --------------------------------------------------

class PlayerInput(BaseModel):
    player_name: str = Field(min_length=1, max_length=40)

class CreateTeamInput(PlayerInput):
    team_name: str | None = Field(default=None, max_length=40)

class JoinTeamInput(PlayerInput):
    join_code: str = Field(min_length=1, max_length=12)


class ActionInput(BaseModel):
    player_id: str = Field(min_length=1)
    answer: str = Field(min_length=1, max_length=200)


# --------------------------------------------------
# Game configuration
# --------------------------------------------------

repository: TeamRepository = create_repository_from_env()

# Each team's timer starts when the second player joins.
# Default duration: 2 hours = 7200 seconds.
GAME_DURATION_SECONDS = max(
    1, int(os.getenv("GAME_DURATION_SECONDS", "7200"))
)

# Combined maximum across both players: 100 points.
STAGE_POINTS = {
    1: {"Analyst": 5, "Monitor": 5},       # 10 points
    2: {"Analyst": 7, "Monitor": 8},       # 15 points
    3: {"Analyst": 7, "Monitor": 8},       # 15 points
    4: {"Analyst": 10, "Monitor": 10},     # 20 points
    5: {"Analyst": 20, "Monitor": 20},     # 40 points
}

_join_code_alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


# --------------------------------------------------
# Timer utilities
# --------------------------------------------------

def utc_now() -> datetime:
    """Return the current UTC time."""
    return datetime.now(timezone.utc)


def _timer_values(team: Team, now: datetime) -> dict:
    """Calculate the shared timer values for a team."""
    if team.started_at is None:
        return {
            "deadline_at": None,
            "elapsed_seconds": 0,
            "remaining_seconds": None,
        }

    deadline = team.started_at + timedelta(
        seconds=team.duration_seconds
    )

    elapsed = max(
        0,
        math.floor((now - team.started_at).total_seconds()),
    )

    remaining = max(
        0,
        math.ceil((deadline - now).total_seconds()),
    )

    return {
        "deadline_at": deadline,
        "elapsed_seconds": elapsed,
        "remaining_seconds": remaining,
    }


def _state_response(team: Team) -> dict:
    """Return team information together with its timer."""
    return {
        **team.model_dump(),
        **_timer_values(team, utc_now()),
    }


def _refresh_team_timer(team_id: str) -> Team:
    """Update a team's status if its timer has expired."""

    def expire_if_needed(team: Team) -> None:
        now = utc_now()

        # Support older Firebase records that use "ready".
        if (
            len(team.players) == 2
            and team.started_at is None
            and team.game_status == "ready"
        ):
            team.started_at = now
            team.game_status = "in_progress"
            team.updated_at = now

        # End the game when the team's two-hour timer expires.
        if (
            team.game_status == "in_progress"
            and team.started_at is not None
            and now >= team.started_at
            + timedelta(seconds=team.duration_seconds)
        ):
            team.game_status = "expired"
            team.completed_at = now
            team.updated_at = now

    team = repository.update(team_id, expire_if_needed)

    if team is None:
        raise HTTPException(
            status_code=404,
            detail="Team was not found",
        )

    return team


# --------------------------------------------------
# CORS configuration
# --------------------------------------------------

def parse_frontend_origins(
    value: str | None = None,
) -> list[str]:
    """Read explicitly configured frontend origins."""
    raw_origins = (
        os.getenv("FRONTEND_ORIGINS", "")
        if value is None
        else value
    )

    origins = [
        origin.strip()
        for origin in raw_origins.split(",")
        if origin.strip()
    ]

    if "*" in origins:
        raise ValueError(
            "FRONTEND_ORIGINS must list specific origins; '*' is not allowed"
        )

    return origins


def configure_cors(
    target_app: FastAPI,
    origins: list[str] | None = None,
) -> None:
    target_app.add_middleware(
        CORSMiddleware,
        allow_origins=(
            parse_frontend_origins()
            if origins is None
            else origins
        ),
        allow_origin_regex=(
            r"^https?://(?:localhost|127\.0\.0\.1)(?::\d+)?$"
        ),
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# --------------------------------------------------
# Application setup
# --------------------------------------------------

def _new_join_code() -> str:
    """Generate a unique six-character team code."""
    while True:
        code = "".join(
            secrets.choice(_join_code_alphabet)
            for _ in range(6)
        )

        if repository.get_by_join_code(code) is None:
            return code


app = FastAPI(title="Don't Trust the System API")
configure_cors(app)


# --------------------------------------------------
# Health endpoints
# --------------------------------------------------

@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "message": "Welcome to the Don't Trust the System API"
    }


@app.get("/health")
def read_health() -> dict[str, str]:
    return {"status": "healthy"}


# --------------------------------------------------
# Team creation and joining
# --------------------------------------------------

@app.post(
    "/teams",
    status_code=status.HTTP_201_CREATED,
)
def create_team(payload: CreateTeamInput) -> dict:
    """Create a team and assign its first player as Analyst."""
    team_id = str(uuid4())
    join_code = _new_join_code()
    now = utc_now()
    team_name = (payload.team_name or "").strip() or (
        f"{payload.player_name.strip()}'s team"
    )
    team = Team(
        team_id=team_id,
        join_code=join_code,
        team_name=team_name,
        players=[
            Player(
                player_id=str(uuid4()),
                player_name=payload.player_name.strip(),
                role="Analyst",
            )
        ],
        duration_seconds=GAME_DURATION_SECONDS,
        created_at=now,
        updated_at=now,
    )

    while not repository.create(team):
        team.join_code = _new_join_code()

    return _state_response(team)


@app.post("/teams/join")
def join_team(payload: JoinTeamInput) -> dict:
    """Join an existing team as Monitor and start its timer."""
    team = repository.get_by_join_code(
        payload.join_code.strip().upper()
    )

    if team is None:
        raise HTTPException(
            status_code=404,
            detail="Team join code was not found",
        )

    monitor = Player(
        player_id=str(uuid4()),
        player_name=payload.player_name.strip(),
        role="Monitor",
    )

    def add_monitor(current: Team) -> None:
        if len(current.players) >= 2:
            raise HTTPException(
                status_code=409,
                detail="Team already has both player roles",
            )

        if any(
            player.role == "Monitor"
            for player in current.players
        ):
            raise HTTPException(
                status_code=409,
                detail="Team already has both player roles",
            )

        now = utc_now()

        current.players.append(monitor)
        current.started_at = now
        current.duration_seconds = GAME_DURATION_SECONDS
        current.game_status = "in_progress"
        current.updated_at = now

    updated = repository.update(team.team_id, add_monitor)

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Team join code was not found",
        )

    return _state_response(updated)


# --------------------------------------------------
# Team state and missions
# --------------------------------------------------

@app.get("/teams/{team_id}/state")
def get_team_state(team_id: str) -> dict:
    return _state_response(
        _refresh_team_timer(team_id)
    )


def _team_and_player(
    team_id: str,
    player_id: str,
) -> tuple[Team, Player]:
    """Find a team and verify that the player belongs to it."""
    team = repository.get(team_id)

    if team is None:
        raise HTTPException(
            status_code=404,
            detail="Team was not found",
        )

    player = next(
        (
            item
            for item in team.players
            if item.player_id == player_id
        ),
        None,
    )

    if player is None:
        raise HTTPException(
            status_code=403,
            detail="Player is not a member of this team",
        )

    return team, player


@app.get("/teams/{team_id}/mission")
def get_mission(
    team_id: str,
    player_id: str,
) -> dict:
    """Return the current mission for the requesting player's role."""
    team = _refresh_team_timer(team_id)

    _, player = _team_and_player(team_id, player_id)

    if team.game_status in {"completed", "expired"}:
        raise HTTPException(
            status_code=409,
            detail="The investigation is already complete",
        )

    return {
        **public_mission(team.current_stage, player.role),
        **_timer_values(team, utc_now()),
    }


# --------------------------------------------------
# Mission answer submission and scoring
# --------------------------------------------------

@app.post("/teams/{team_id}/actions")
def submit_action(
    team_id: str,
    payload: ActionInput,
) -> dict:
    """Validate an answer, award points, and advance the team."""
    submitted_stage: int | None = None
    expired = False
    points_awarded = 0

    def apply_submission(team: Team) -> None:
        nonlocal submitted_stage, expired, points_awarded

        player = next(
            (
                item
                for item in team.players
                if item.player_id == payload.player_id
            ),
            None,
        )

        if player is None:
            raise HTTPException(
                status_code=403,
                detail="Player is not a member of this team",
            )

        if len(team.players) < 2:
            raise HTTPException(
                status_code=409,
                detail="Both players must join before missions can progress",
            )

        if team.game_status == "completed":
            raise HTTPException(
                status_code=409,
                detail="The investigation is already complete",
            )

        if team.game_status == "expired":
            expired = True
            return

        now = utc_now()

        if team.started_at is None:
            raise HTTPException(
                status_code=409,
                detail="The game timer has not started",
            )

        deadline = team.started_at + timedelta(
            seconds=team.duration_seconds
        )

        if now >= deadline:
            team.game_status = "expired"
            team.completed_at = now
            team.updated_at = now
            expired = True
            return

        stage = team.current_stage
        action_id = f"stage-{stage}:{player.role.lower()}"

        if action_id in team.completed_actions:
            raise HTTPException(
                status_code=409,
                detail="This player's stage action is already complete",
            )

        answer_key = MISSIONS[stage]["roles"][player.role]["answer_key"]

        if payload.answer.strip().casefold() != answer_key.casefold():
            raise HTTPException(
                status_code=400,
                detail="The submitted answer is incorrect",
            )

        submitted_stage = stage
        team.completed_actions.append(action_id)

        # Award the points assigned to this stage and role.
        points_awarded = STAGE_POINTS[stage][player.role]
        team.score += points_awarded

        stage_actions = {
            f"stage-{stage}:analyst",
            f"stage-{stage}:monitor",
        }

        # Both players must submit correct answers to complete a stage.
        if stage_actions.issubset(team.completed_actions):
            team.completed_stages.append(stage)

            if stage == len(MISSIONS):
                team.game_status = "completed"
                team.completed_at = now
            else:
                team.current_stage += 1

        team.updated_at = now

    updated = repository.update(
        team_id,
        apply_submission,
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Team was not found",
        )

    if expired:
        raise HTTPException(
            status_code=409,
            detail="The game time has expired",
        )

    assert submitted_stage is not None

    completed_actions = {
        f"stage-{submitted_stage}:analyst",
        f"stage-{submitted_stage}:monitor",
    }

    stage_completed = completed_actions.issubset(
        updated.completed_actions
    )

    return {
        "accepted": True,
        "points_awarded": points_awarded,
        "score": updated.score,
        "stage_completed": stage_completed,
        "completed_stages": updated.completed_stages,
        "current_stage": updated.current_stage,
        "game_status": updated.game_status,
        **_timer_values(updated, utc_now()),
    }


# --------------------------------------------------
# Team results
# --------------------------------------------------

@app.get("/teams/{team_id}/results")
def get_team_results(team_id: str) -> dict:
    """Return the team's current score and completion status."""
    team = _refresh_team_timer(team_id)

    return {
        "team_id": team.team_id,
        "score": team.score,
        "completed_stages": team.completed_stages,
        "game_status": team.game_status,
        "final": team.game_status in {"completed", "expired"},
        **_timer_values(team, utc_now()),
    }
# --------------------------------------------------
# Leaderboard
# --------------------------------------------------

@app.get("/leaderboard")
def get_leaderboard() -> list[dict]:
    """Public ranking: score descending, then time taken ascending."""
    now = utc_now()
    rows = []

    for team in repository.list_all():
        if team.started_at is None:
            time_taken = 0
        else:
            deadline = team.started_at + timedelta(
                seconds=team.duration_seconds
            )
            end = team.completed_at or min(now, deadline)
            time_taken = max(
                0, math.floor((end - team.started_at).total_seconds())
            )

        rows.append(
            {
                "team_name": team.team_name or "Unnamed team",
                "score": team.score,
                "current_stage": team.current_stage,
                "game_status": team.game_status,
                "time_taken_seconds": time_taken,
            }
        )

    rows.sort(key=lambda row: (-row["score"], row["time_taken_seconds"]))

    return [{"rank": index, **row} for index, row in enumerate(rows, start=1)]
