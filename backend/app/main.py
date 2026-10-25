from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import math
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from backend.app.repository import TeamRepository, create_repository_from_env
from backend.app.missions import (
    MISSIONS,
    public_mission,
    find_question,
    is_unlocked,
    check_answer,
    visible_assets,
    find_asset,
)
from backend.app.models import Player, Team
from backend.app.terminal import run_command, has_terminal


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
    question_id: str = Field(min_length=1, max_length=20)
    answer: str = Field(min_length=1, max_length=200)


class HintInput(BaseModel):
    player_id: str = Field(min_length=1)
    question_id: str = Field(min_length=1, max_length=20)


class TerminalInput(BaseModel):
    player_id: str = Field(min_length=1)
    command: str = Field(min_length=1, max_length=200)
    cwd: str = Field(default="/", max_length=200)


# --------------------------------------------------
# Game configuration
# --------------------------------------------------

repository: TeamRepository = create_repository_from_env()

# Each team's timer starts when the second player joins. Default: 90 minutes.
GAME_DURATION_SECONDS = max(1, int(os.getenv("GAME_DURATION_SECONDS", "5400")))

TOTAL_STAGES = 5
MAX_WRONG_BEFORE_LOCK = 5
LOCK_SECONDS = 30
HINT_COST = 1
STAGE5_SECONDS = int(os.getenv("STAGE5_SECONDS", "480"))
STAGE5_DELETED_SECONDS = 360
DATA_LOST_PENALTY = 5

# TESTING ONLY: START_STAGE=2 in .env makes new teams start at stage 2.
# Remove this line from .env before the event!
START_STAGE = min(max(1, int(os.getenv("START_STAGE", "1"))), TOTAL_STAGES)
if START_STAGE != 1:
    print(f"WARNING: START_STAGE={START_STAGE}. New teams skip ahead. Remove before the event!")

ASSET_DIR = Path(__file__).parent / "assets"

_join_code_alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


# --------------------------------------------------
# Timer utilities
# --------------------------------------------------

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _timer_values(team: Team, now: datetime) -> dict:
    if team.started_at is None:
        return {
            "deadline_at": None,
            "elapsed_seconds": 0,
            "remaining_seconds": None,
        }

    deadline = team.started_at + timedelta(seconds=team.duration_seconds)
    elapsed = max(0, math.floor((now - team.started_at).total_seconds()))
    remaining = max(0, math.ceil((deadline - now).total_seconds()))

    return {
        "deadline_at": deadline,
        "elapsed_seconds": elapsed,
        "remaining_seconds": remaining,
    }


def _stage5_total(team: Team) -> int:
    return STAGE5_DELETED_SECONDS if "3:deleted" in team.flags else STAGE5_SECONDS


def _stage5_values(team: Team, now: datetime) -> dict:
    if team.current_stage != TOTAL_STAGES or team.stage_started_at is None:
        return {"countdown_seconds": None, "countdown_total": None}
    total = _stage5_total(team)
    end = team.stage_started_at + timedelta(seconds=total)
    return {"countdown_seconds": max(0, math.ceil((end - now).total_seconds())),
               "countdown_total": total}

def _state_response(team: Team) -> dict:
    return {**team.model_dump(), **_timer_values(team, utc_now()), **_stage5_values(team, utc_now())}


def _refresh_team_timer(team_id: str) -> Team:
    """Update a team's status if its timer has expired."""

    def expire_if_needed(team: Team) -> None:
        now = utc_now()
        if (team.current_stage == TOTAL_STAGES and team.game_status == "in_progress"
                   and team.started_at is not None):
            if team.stage_started_at is None:
                   team.stage_started_at = now
            elif now >= team.stage_started_at + timedelta(seconds=_stage5_total(team)):
                   team.game_status = "completed"
                   team.outcome = "data_lost"
                   team.score = max(0, team.score - DATA_LOST_PENALTY)
                   team.completed_at = now
                   team.updated_at = now


        # Support older records that use "ready".
        if (
            len(team.players) == 2
            and team.started_at is None
            and team.game_status == "ready"
        ):
            team.started_at = now
            team.game_status = "in_progress"
            team.updated_at = now

        if (
            team.game_status == "in_progress"
            and team.started_at is not None
            and now >= team.started_at + timedelta(seconds=team.duration_seconds)
        ):
            team.game_status = "expired"
            team.completed_at = now
            team.updated_at = now

    team = repository.update(team_id, expire_if_needed)

    if team is None:
        raise HTTPException(status_code=404, detail="Team was not found")

    return team


# --------------------------------------------------
# CORS configuration
# --------------------------------------------------

def parse_frontend_origins(value: str | None = None) -> list[str]:
    raw_origins = os.getenv("FRONTEND_ORIGINS", "") if value is None else value

    origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

    if "*" in origins:
        raise ValueError(
            "FRONTEND_ORIGINS must list specific origins; '*' is not allowed"
        )

    return origins


def configure_cors(target_app: FastAPI, origins: list[str] | None = None) -> None:
    target_app.add_middleware(
        CORSMiddleware,
        allow_origins=(parse_frontend_origins() if origins is None else origins),
        allow_origin_regex=r"^https?://(?:localhost|127\.0\.0\.1)(?::\d+)?$",
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# --------------------------------------------------
# Application setup
# --------------------------------------------------

def _new_join_code() -> str:
    while True:
        code = "".join(secrets.choice(_join_code_alphabet) for _ in range(6))
        if repository.get_by_join_code(code) is None:
            return code


app = FastAPI(title="Don't Trust the System API")
configure_cors(app)


# --------------------------------------------------
# Health endpoints
# --------------------------------------------------

@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse("/play/")


@app.get("/health")
def read_health() -> dict[str, str]:
    return {"status": "healthy"}


# --------------------------------------------------
# Team creation and joining
# --------------------------------------------------

@app.post("/teams", status_code=status.HTTP_201_CREATED)
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
        current_stage=START_STAGE,
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
    team = repository.get_by_join_code(payload.join_code.strip().upper())

    if team is None:
        raise HTTPException(status_code=404, detail="Team join code was not found")

    monitor = Player(
        player_id=str(uuid4()),
        player_name=payload.player_name.strip(),
        role="Monitor",
    )

    def add_monitor(current: Team) -> None:
        if len(current.players) >= 2:
            raise HTTPException(
                status_code=409, detail="Team already has both player roles"
            )

        if any(player.role == "Monitor" for player in current.players):
            raise HTTPException(
                status_code=409, detail="Team already has both player roles"
            )

        now = utc_now()

        current.players.append(monitor)
        current.started_at = now
        current.duration_seconds = GAME_DURATION_SECONDS
        current.game_status = "in_progress"
        current.updated_at = now

    updated = repository.update(team.team_id, add_monitor)

    if updated is None:
        raise HTTPException(status_code=404, detail="Team join code was not found")

    return _state_response(updated)


# --------------------------------------------------
# Team state and missions
# --------------------------------------------------

@app.get("/teams/{team_id}/state")
def get_team_state(team_id: str) -> dict:
    return _state_response(_refresh_team_timer(team_id))


def _team_and_player(team_id: str, player_id: str) -> tuple[Team, Player]:
    team = repository.get(team_id)

    if team is None:
        raise HTTPException(status_code=404, detail="Team was not found")

    player = next((p for p in team.players if p.player_id == player_id), None)

    if player is None:
        raise HTTPException(
            status_code=403, detail="Player is not a member of this team"
        )

    return team, player


@app.get("/teams/{team_id}/mission")
def get_mission(team_id: str, player_id: str) -> dict:
    """Return the current mission for the requesting player's role."""
    team = _refresh_team_timer(team_id)

    _, player = _team_and_player(team_id, player_id)

    if team.game_status in {"completed", "expired"}:
        raise HTTPException(
            status_code=409, detail="The investigation is already complete"
        )

    return {
        **public_mission(team.current_stage, player.role, team.answered, team.flags),
        "terminal": has_terminal(team.current_stage, player.role),
        "assets": visible_assets(team.current_stage, player.role, team.answered, team.flags),
        **_timer_values(team, utc_now()),
    }


# --------------------------------------------------
# Answer submission, attempt limits and hints
# --------------------------------------------------

def _stage_done(team: Team, stage: int) -> bool:
    for role, data in MISSIONS[stage]["roles"].items():
        for q in data["questions"]:
            if not team.answered.get(f"{stage}:{role}:{q['id']}"):
                return False
    return True


@app.post("/teams/{team_id}/actions")
def submit_action(team_id: str, payload: ActionInput) -> dict:
    _refresh_team_timer(team_id)
    
    """Validate an answer, award points, and advance the team."""
    # Errors for wrong/locked/expired are raised AFTER the update, because
    # raising inside the updater would throw away the saved attempt counts.
    outcome = {"result": None, "wait": 0, "points": 0, "penalty": 0, "stage": None, "left": 0}
    def apply(team: Team) -> None:
        player = next(
            (p for p in team.players if p.player_id == payload.player_id), None
        )
        if player is None:
            raise HTTPException(
                status_code=403, detail="Player is not a member of this team"
            )
        if len(team.players) < 2 or team.started_at is None:
            raise HTTPException(
                status_code=409,
                detail="Both players must join before missions can progress",
            )
        if team.game_status == "completed":
            raise HTTPException(
                status_code=409, detail="The investigation is already complete"
            )

        now = utc_now()

        if team.game_status == "expired" or now >= team.started_at + timedelta(
            seconds=team.duration_seconds
        ):
            if team.game_status != "expired":
                team.game_status = "expired"
                team.completed_at = now
                team.updated_at = now
            outcome["result"] = "expired"
            return

        stage = team.current_stage
        q = find_question(stage, player.role, payload.question_id)

        if q is None or not is_unlocked(stage, player.role, q, team.answered):
            raise HTTPException(status_code=404, detail="Question not available")

        key = f"{stage}:{player.role}:{q['id']}"

        if team.answered.get(key):
            raise HTTPException(status_code=409, detail="Already answered")

        lock = team.locked_until.get(key)
        if lock and now < lock:
            outcome["result"] = "locked"
            outcome["wait"] = math.ceil((lock - now).total_seconds())
            return

        if not check_answer(q, payload.answer):
            n = team.wrong_attempts.get(key, 0) + 1
            team.wrong_attempts[key] = n
            if n % MAX_WRONG_BEFORE_LOCK == 0:
                wait = LOCK_SECONDS * (n // MAX_WRONG_BEFORE_LOCK)
                team.locked_until[key] = now + timedelta(seconds=wait)
                outcome["wait"] = wait
            outcome["result"] = "wrong"
            outcome["left"] = MAX_WRONG_BEFORE_LOCK - (n % MAX_WRONG_BEFORE_LOCK)
            team.updated_at = now
            return

        effect = q.get("effects", {}).get(payload.answer.strip().casefold(), {})
        gained = effect.get("points", q["points"])
        penalty = effect.get("penalty", 0)

        team.answered[key] = True
        team.score = max(0, team.score + gained - penalty)
        if effect.get("flag"):
            team.flags.append(f"{stage}:{effect['flag']}")
        outcome["points"] = gained
        outcome["penalty"] = penalty
        outcome["result"] = "correct"
        outcome["stage"] = stage

        if _stage_done(team, stage):
            team.completed_stages.append(stage)
            if stage >= TOTAL_STAGES:
                team.game_status = "completed"
                team.completed_at = now
                team.outcome = "partial" if "5:insider_wrong" in team.flags else "full"
            else:
                team.current_stage += 1

        team.updated_at = now
    updated = repository.update(team_id, apply)

    if updated is None:
        raise HTTPException(status_code=404, detail="Team was not found")

    result = outcome["result"]

    if result == "expired":
        raise HTTPException(status_code=409, detail="The game time has expired")

    if result == "locked":
        raise HTTPException(
            status_code=429,
            detail=f"Too many wrong answers. Try again in {outcome['wait']}s",
        )

    if result == "wrong":
        message = "The submitted answer is incorrect."
        if outcome["wait"]:
            message += f" Locked for {outcome['wait']}s."
        else:
            message += f" {outcome['left']} tries left before a lockout."
        raise HTTPException(status_code=400, detail=message)

    return {
        "accepted": True,
        "points_awarded": outcome["points"],
        "penalty": outcome["penalty"],
        "score": updated.score,
        "stage_completed": outcome["stage"] in updated.completed_stages,
        "completed_stages": updated.completed_stages,
        "current_stage": updated.current_stage,
        "game_status": updated.game_status,
        **_timer_values(updated, utc_now()),
    }


@app.post("/teams/{team_id}/hint")
def get_hint(team_id: str, payload: HintInput) -> dict:
    """Release a hint. The first hint per question costs HINT_COST points."""
    out = {"hint": None, "score": 0}

    def apply(team: Team) -> None:
        player = next(
            (p for p in team.players if p.player_id == payload.player_id), None
        )
        if player is None:
            raise HTTPException(
                status_code=403, detail="Player is not a member of this team"
            )

        q = find_question(team.current_stage, player.role, payload.question_id)

        if q is None or not is_unlocked(
            team.current_stage, player.role, q, team.answered
        ):
            raise HTTPException(status_code=404, detail="Question not available")

        key = f"{team.current_stage}:{player.role}:{q['id']}"

        if key not in team.hints_used:
            team.hints_used.append(key)
            team.score = max(0, team.score - HINT_COST)
            team.updated_at = utc_now()

        out["hint"] = q["hint"]
        out["score"] = team.score

    if repository.update(team_id, apply) is None:
        raise HTTPException(status_code=404, detail="Team was not found")

    return out


# --------------------------------------------------
# Fake terminal and image attachments
# --------------------------------------------------

@app.post("/teams/{team_id}/terminal")
def run_terminal(team_id: str, payload: TerminalInput) -> dict:
    """Run a read-only fake terminal command for the player's current stage."""
    team = _refresh_team_timer(team_id)
    _, player = _team_and_player(team_id, payload.player_id)

    if team.game_status != "in_progress":
        raise HTTPException(status_code=409, detail="The game is not in progress")

    output, cwd, prompt = run_command(
        team.current_stage, player.role, team.answered, team.flags,
        payload.command, payload.cwd
    )
    return {"output": output, "cwd": cwd, "prompt": prompt}


@app.get("/teams/{team_id}/asset/{asset_id}")
def get_asset(team_id: str, asset_id: str, player_id: str):
    """Serve an attachment (like a QR code) only once it is unlocked."""
    team, player = _team_and_player(team_id, player_id)

    if team.game_status != "in_progress":
        raise HTTPException(status_code=409, detail="The game is not in progress")

    asset = find_asset(team.current_stage, player.role, asset_id, team.answered, team.flags)
    path = ASSET_DIR / asset["file"] if asset else None

    if asset is None or not path.is_file():
        raise HTTPException(status_code=404, detail="Attachment not available")

    return FileResponse(
        path, media_type="image/png", headers={"Cache-Control": "no-store"}
    )


# --------------------------------------------------
# Team results
# --------------------------------------------------

@app.get("/teams/{team_id}/results")
def get_team_results(team_id: str) -> dict:
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
            deadline = team.started_at + timedelta(seconds=team.duration_seconds)
            end = team.completed_at or min(now, deadline)
            time_taken = max(0, math.floor((end - team.started_at).total_seconds()))

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


# --------------------------------------------------
# Game pages (must stay last)
# --------------------------------------------------

app.mount(
    "/play",
    StaticFiles(directory=Path(__file__).parent / "static", html=True),
    name="play",
)