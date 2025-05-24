from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "user"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    token: UUID | None = Field(default_factory=uuid4)
    email: EmailStr = Field(sa_column=Column(String, unique=True, nullable=False))
    password: str
    stats: List["Stats"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Stats(SQLModel, table=True):
    __tablename__ = "stats"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    value: Decimal = Field(default=0, max_digits=4, decimal_places=1)
    user_id: UUID | None = Field(default=None, foreign_key="user.id")
    user: User | None = Relationship(back_populates="stats")


class StatAddRequest(BaseModel):
    value: Decimal


class StatImportEntry(BaseModel):
    timestamp: int | str
    value: Decimal


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str
