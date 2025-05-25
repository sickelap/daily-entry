from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel


class UserEntity(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore
    id: int | None = Field(primary_key=True, default=None)
    token: UUID | None = Field(default_factory=uuid4)
    email: EmailStr = Field(sa_column=Column(String, unique=True, nullable=False))
    password: str
    metrics: list["MetricEntity"] = Relationship(back_populates="user")
    values: list["ValueEntity"] = Relationship(back_populates="user")


class MetricEntity(SQLModel, table=True):
    __table_name__ = "metrics"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="users.id")
    user: UserEntity = Relationship(back_populates="metrics")
    name: str = Field(index=True)
    # values: list["ValueEntity"] = Relationship(back_populates="metric")


class ValueEntity(SQLModel, table=True):
    __tablename__ = "values"  # type: ignore
    id: int | None = Field(primary_key=True, default=None)
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now(timezone.utc).timestamp())
    )
    value: Decimal = Field(default=0, max_digits=4, decimal_places=1)
    user_id: int = Field(foreign_key="users.id")
    user: UserEntity = Relationship(back_populates="values")
    # metric_id: int | None = Field(default=None, foreign_key="metrics.id")
    # metric: MetricEntity | None = Relationship(back_populates="values")


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


class CreateMetricRequest(BaseModel):
    name: str


class MetricResponse(BaseModel):
    name: str
