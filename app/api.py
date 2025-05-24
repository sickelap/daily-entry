from typing import Annotated, List

from app.config import AUTH_HEADER
from app.db import get_session
from app.model import (
    StatEntry,
    StatImportEntry,
    UserEntity,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.service import (
    add_user_stat,
    create_user,
    get_user,
    get_user_token,
    import_user_stats,
    rotate_user_token,
)
from fastapi import APIRouter, Body, Depends, Response
from sqlmodel import Session

router = APIRouter()


@router.get("/stats")
async def get_stats(user: Annotated[UserEntity, Depends(get_user)]):
    return user.stats


@router.post("/stats")
async def add_stat(
    user: Annotated[UserEntity, Depends(get_user)],
    db: Annotated[Session, Depends(get_session)],
    payload: StatEntry,
):
    return add_user_stat(db, user, payload)


@router.post("/import")
async def import_stats(
    user: Annotated[UserEntity, Depends(get_user)],
    db: Annotated[Session, Depends(get_session)],
    payload: Annotated[List[StatImportEntry], Body()],
):
    return import_user_stats(db, user, payload)


@router.post("/register")
async def register(
    db: Annotated[Session, Depends(get_session)], payload: UserRegisterRequest
):
    token = create_user(db, payload)
    return Response(status_code=201, headers={AUTH_HEADER: token})


@router.post("/token")
async def login(
    db: Annotated[Session, Depends(get_session)], payload: UserLoginRequest
):
    token = get_user_token(db, payload)
    return {AUTH_HEADER: token}


@router.post("/token/rotate")
async def rotate_token(
    user: Annotated[UserEntity, Depends(get_user)],
    db: Annotated[Session, Depends(get_session)],
):
    new_token = rotate_user_token(db, user)
    return {AUTH_HEADER: new_token}
