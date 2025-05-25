from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel


class UserEntity(SQLModel, table=True):
    __tablename__ = "user"  # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    token: UUID | None = Field(default_factory=uuid4)
    email: EmailStr = Field(sa_column=Column(String, unique=True, nullable=False))
    password: str
    stats: List["StatsEntity"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )


class StatsEntity(SQLModel, table=True):
    __tablename__ = "stats"  # type: ignore
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    value: Decimal = Field(default=0, max_digits=4, decimal_places=1)
    user_id: UUID | None = Field(default=None, foreign_key="user.id")
    user: UserEntity | None = Relationship(back_populates="stats")


class AddStatRequest(BaseModel):
    value: Decimal


class Stat(BaseModel):
    timestamp: Optional[int | str]
    value: Decimal


class EmailAndPassword(BaseModel):
    email: EmailStr
    password: str


class UserRegisterRequest(EmailAndPassword):
    pass


class UserLoginRequest(EmailAndPassword):
    pass
