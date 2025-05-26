import string
import secrets
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Annotated, Optional, Sequence, cast
from uuid import UUID
from dateutil import parser
from jose import jwt
from fastapi.security import OAuth2PasswordBearer

from app import config, exceptions
from app.db import get_session
from app.model import (
    CreateMetricRequest,
    EmailAndPassword,
    MetricEntity,
    Tokens,
    UserEntity,
    UserRegisterRequest,
    ValueEntity,
    ValueRequest,
)
from fastapi import Depends
from passlib.context import CryptContext
from sqlmodel import Session, select


crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{config.API_PREFIX}{config.LOGIN_URI}")


def hash_password(plaintext: str) -> str:
    return crypt_context.hash(plaintext)


def verify_password(plaintext: str, hashed: str) -> bool:
    return crypt_context.verify(plaintext, hashed)


def create_token(user_id: UUID, token_type: str, expires_delta: timedelta) -> str:
    alphabet = string.ascii_letters + string.digits
    rnd = "".join(secrets.choice(alphabet) for _ in range(config.JWT_JTI_LEN))
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {"exp": expire, "typ": token_type, "sub": str(user_id), "rnd": rnd}
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.JWT_ALGORITHM)


def create_access_token(user_id: UUID) -> str:
    return create_token(
        user_id, "access", timedelta(minutes=config.JWT_ACCESS_EXPIRES_MINUTES)
    )


def create_refresh_token(user_id: UUID) -> str:
    return create_token(
        user_id, "refresh", timedelta(days=config.JWT_REFRESH_EXPIRES_DAYS)
    )


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
    except Exception:
        raise exceptions.InvalidToken


def verify_token(token, token_type) -> UUID:
    try:
        data = decode_token(token)
    except Exception:
        raise exceptions.InvalidToken()
    if data.get("typ") != token_type:
        raise exceptions.InvalidToken()
    user_id = data.get("sub")
    return UUID(user_id)


def get_user(
    db: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> Optional[UserEntity]:
    user_id = verify_token(token, "access")
    stmt = select(UserEntity).where(UserEntity.id == user_id)
    user = db.exec(stmt).one_or_none()
    if not user:
        raise exceptions.Unauthorized()
    return user


def get_metric(
    user: Annotated[UserEntity, Depends(get_user)],
    db: Annotated[Session, Depends(get_session)],
    metric_id: UUID,
) -> Optional[MetricEntity]:
    stmt = (
        select(MetricEntity)
        .where(MetricEntity.user == user)
        .where(MetricEntity.id == metric_id)
    )
    metric = db.exec(stmt).one_or_none()
    if not metric:
        raise exceptions.NotFound("metric not found")
    return metric


def login(db: Session, request: EmailAndPassword) -> Tokens:
    stmt = select(UserEntity).where(UserEntity.email == request.email)
    user = db.exec(stmt).one_or_none()
    if not user or not verify_password(request.password, user.password):
        raise exceptions.Unauthorized()
    return Tokens(
        access_token=create_access_token(cast(UUID, user.id)),
        refresh_token=create_refresh_token(cast(UUID, user.id)),
    )


def create_user(db: Session, payload: UserRegisterRequest):
    stmt = select(UserEntity).where(UserEntity.email == payload.email)
    user = db.exec(stmt).one_or_none()
    if user:
        raise exceptions.EmailAlreadyExist
    user = UserEntity(email=payload.email, password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return Tokens(
        access_token=create_access_token(cast(UUID, user.id)),
        refresh_token=create_refresh_token(cast(UUID, user.id)),
    )


def refresh_token(token: str) -> Tokens:
    user_id = verify_token(token, "refresh")
    return Tokens(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


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


def get_values(db: Session, metric: MetricEntity):
    stmt = select(ValueEntity).where(ValueEntity.metric == metric)
    return db.exec(stmt).all()
