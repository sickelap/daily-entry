from typing import Annotated, List, Optional
from uuid import UUID

from app import exceptions
from app.db import get_session
from app.model import StatAddRequest, StatImportEntry, Stats, User, UserRegisterRequest
from dateutil import parser
from fastapi import Depends, Header, HTTPException
from passlib.context import CryptContext
from sqlmodel import Session, select

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plaintext: str) -> str:
    return crypt_context.hash(plaintext)


# def veryfy_password(plaintext: str, hashed: str) -> bool:
#     return crypt_context.verify(plaintext, hashed)


def get_user(
    db: Annotated[Session, Depends(get_session)],
    token: Annotated[str | None, Header()] = None,
) -> Optional[User]:
    if not token:
        raise HTTPException(status_code=403)
    stmt = select(User).where(User.token == UUID(token))
    user = db.exec(stmt).one_or_none()
    if not user:
        raise HTTPException(status_code=403)
    return user


def add_user_stat(db: Session, user: User, payload: StatAddRequest):
    stat = Stats(user=user, value=payload.value)
    db.add(stat)
    db.commit()


def import_user_stats(db: Session, user: User, payload: List[StatImportEntry]):
    for entry in payload:
        if isinstance(entry.timestamp, str):
            timestamp = int(parser.parse(entry.timestamp, dayfirst=True).timestamp())
        else:
            timestamp = entry.timestamp
        stat = Stats(user=user, value=entry.value, timestamp=timestamp)
        db.add(stat)
    db.commit()


def create_user(db: Session, payload: UserRegisterRequest) -> str:
    stmt = select(User).where(User.email == payload.email)
    user = db.exec(stmt).one_or_none()
    if user:
        raise exceptions.EmailAlreadyExist
    user = User(email=payload.email, password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return str(user.token)
