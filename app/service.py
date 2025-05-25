from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated, Optional, Sequence
from uuid import UUID, uuid4
from dateutil import parser

from app import exceptions
from app.db import get_session
from app.model import (
    CreateMetricRequest,
    MetricEntity,
    UserEntity,
    UserLoginRequest,
    UserRegisterRequest,
    ValueEntity,
    ValueRequest,
)
from fastapi import Depends, Header, HTTPException
from passlib.context import CryptContext
from sqlmodel import Session, select

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plaintext: str) -> str:
    return crypt_context.hash(plaintext)


def verify_password(plaintext: str, hashed: str) -> bool:
    return crypt_context.verify(plaintext, hashed)


def get_user(
    db: Annotated[Session, Depends(get_session)],
    token: Annotated[str | None, Header()] = None,
) -> Optional[UserEntity]:
    if not token:
        raise HTTPException(status_code=401)
    stmt = select(UserEntity).where(UserEntity.token == UUID(token))
    user = db.exec(stmt).one_or_none()
    if not user:
        raise HTTPException(status_code=403)
    return user


def get_metric(
    user: Annotated[UserEntity, Depends(get_user)],
    db: Annotated[Session, Depends(get_session)],
    metric_id,
) -> Optional[MetricEntity]:
    stmt = (
        select(MetricEntity)
        .where(MetricEntity.user == user)
        .where(MetricEntity.id == metric_id)
    )
    metric = db.exec(stmt).one_or_none()
    if not metric:
        raise HTTPException(status_code=404, detail="metric not found")
    return metric


def create_user(db: Session, payload: UserRegisterRequest) -> str:
    stmt = select(UserEntity).where(UserEntity.email == payload.email)
    user = db.exec(stmt).one_or_none()
    if user:
        raise exceptions.EmailAlreadyExist
    user = UserEntity(email=payload.email, password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return str(user.token)


def get_user_token(db: Session, payload: UserLoginRequest) -> str:
    stmt = select(UserEntity).where(UserEntity.email == payload.email)
    user = db.exec(stmt).one_or_none()
    if not user or not verify_password(payload.password, user.password):
        raise exceptions.InvalidCredentials
    return str(user.token)


def rotate_user_token(db: Session, user: UserEntity) -> str:
    user.token = uuid4()
    db.add(user)
    db.commit()
    db.refresh(user)
    return str(user.token)


def create_metric(
    db: Session, user: UserEntity, payload: CreateMetricRequest
) -> MetricEntity:
    metric = MetricEntity(user=user, name=payload.name)
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


def get_metrics(db: Session, user: UserEntity) -> Sequence[MetricEntity]:
    stmt = select(MetricEntity).where(MetricEntity.user == user)
    return db.exec(stmt).all()


def _create_value_entity(
    metric: MetricEntity, value: Decimal, timestamp: Optional[int | str] = None
) -> ValueEntity:
    if timestamp is None:
        timestamp = int(datetime.now(timezone.utc).timestamp())
    elif isinstance(timestamp, str):
        timestamp = int(parser.parse(timestamp, dayfirst=True).timestamp())
    return ValueEntity(metric=metric, value=value, timestamp=timestamp)


def add_values(db: Session, metric: MetricEntity, payload: list[ValueRequest]):
    for entry in payload:
        stat = _create_value_entity(metric, entry.value, timestamp=entry.timestamp)
        db.add(stat)
    db.commit()
