from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated, List, Optional
from uuid import UUID, uuid4

from app import exceptions
from app.db import get_session
from app.model import (
    AddStatRequest,
    Stat,
    StatsEntity,
    UserEntity,
    UserLoginRequest,
    UserRegisterRequest,
)
from dateutil import parser
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
        raise HTTPException(status_code=403)
    stmt = select(UserEntity).where(UserEntity.token == UUID(token))
    user = db.exec(stmt).one_or_none()
    if not user:
        raise HTTPException(status_code=403)
    return user


def _create_stat_entity(
    user: UserEntity, value: Decimal, timestamp: Optional[int | str] = None
) -> StatsEntity:
    if isinstance(timestamp, str):
        timestamp = int(parser.parse(timestamp, dayfirst=True).timestamp())
    elif isinstance(timestamp, int):
        timestamp = timestamp
    else:
        timestamp = int(datetime.now(timezone.utc).timestamp())
    return StatsEntity(user=user, value=value, timestamp=timestamp)


def add_user_stat(db: Session, user: UserEntity, payload: AddStatRequest):
    stat = _create_stat_entity(user=user, value=payload.value)
    db.add(stat)
    db.commit()


def import_user_stats(db: Session, user: UserEntity, payload: List[Stat]):
    for entry in payload:
        stat = _create_stat_entity(user, entry.value, timestamp=entry.timestamp)
        db.add(stat)
    db.commit()


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
