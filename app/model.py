from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel


class UserEntity(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore
    id: UUID | None = Field(primary_key=True, default_factory=uuid4)
    token: UUID | None = Field(default_factory=uuid4)
    email: EmailStr = Field(sa_column=Column(String, unique=True, nullable=False))
    password: str
    metrics: list["MetricEntity"] = Relationship(back_populates="user")


class MetricEntity(SQLModel, table=True):
    __tablename__ = "metrics"  # type: ignore
    id: UUID | None = Field(primary_key=True, default_factory=uuid4)
    user_id: UUID = Field(default=None, foreign_key="users.id")
    user: UserEntity = Relationship(back_populates="metrics")
    name: str = Field(index=True)
    values: list["ValueEntity"] = Relationship(
        back_populates="metric", cascade_delete=True
    )


class ValueEntity(SQLModel, table=True):
    __tablename__ = "values"  # type: ignore
    id: UUID | None = Field(primary_key=True, default_factory=uuid4)
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now(timezone.utc).timestamp())
    )
    value: Decimal = Field(default=0, max_digits=4, decimal_places=1)
    metric_id: Optional[UUID] = Field(
        default=None, foreign_key="metrics.id", ondelete="CASCADE"
    )
    metric: MetricEntity = Relationship(back_populates="values")


class ValueRequest(BaseModel):
    value: Decimal
    timestamp: Optional[int | str] = None


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
    id: UUID
    name: str


class AccessToken(BaseModel):
    access_token: Optional[str] = None


class RefreshToken(BaseModel):
    refresh_token: str


class Tokens(AccessToken, RefreshToken):
    pass
