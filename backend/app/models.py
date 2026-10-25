"""Shared Pydantic models for persisted team and player state."""

from datetime import datetime

from pydantic import BaseModel, Field


class Player(BaseModel):
    player_id: str
    player_name: str
    role: str


class Team(BaseModel):
    team_id: str
    join_code: str
    team_name: str = ""
    players: list[Player]
    current_stage: int = 1
    game_status: str = "waiting_for_players"
    score: int = 0
    completed_actions: list[str] = Field(default_factory=list)
    completed_stages: list[int] = Field(default_factory=list)
    answered: dict[str, bool] = Field(default_factory=dict)
    wrong_attempts: dict[str, int] = Field(default_factory=dict)
    locked_until: dict[str, datetime] = Field(default_factory=dict)
    hints_used: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    duration_seconds: int = 5400
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime