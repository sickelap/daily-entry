import uuid
from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class UserBase(SQLModel):
    id: UUID
    token: str


class User(UserBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    token: str
    stats: List["Stats"] = Relationship(back_populates="user")


class StatsBase(SQLModel):
    timestamp: int
    value: Decimal


class Stats(StatsBase, table=True):
    id: int = Field(primary_key=True)
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    value: Decimal = Field(default=0, max_digits=4, decimal_places=1)
    user_id: UUID | None = Field(default=None, foreign_key="user.id")
    user: User | None = Relationship(back_populates="stats")
