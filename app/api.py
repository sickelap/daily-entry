from typing import Annotated, List
from app import config
from app.db import get_session
from app.model import (
    AddStatRequest,
    CreateMetricRequest,
    MetricResponse,
    Stat,
    UserEntity,
    UserLoginRequest,
    UserRegisterRequest,
)
from app import service
from fastapi import APIRouter, Depends, Response
from sqlmodel import Session

router = APIRouter(prefix=config.API_PREFIX)


@router.get(config.GET_STATS_URI)
async def get_stats(user: Annotated[UserEntity, Depends(service.get_user)]):
    return user.values


@router.post(config.ADD_STAT_URI)
async def add_stat(
    user: Annotated[UserEntity, Depends(service.get_user)],
    db: Annotated[Session, Depends(get_session)],
    payload: AddStatRequest,
):
    return service.add_user_stat(db, user, payload)


@router.post(config.IMPORT_STATS_URI)
async def import_stats(
    user: Annotated[UserEntity, Depends(service.get_user)],
    db: Annotated[Session, Depends(get_session)],
    payload: List[Stat],
):
    return service.import_user_stats(db, user, payload)


@router.post(config.REGISTER_URI)
async def register(
    db: Annotated[Session, Depends(get_session)], payload: UserRegisterRequest
):
    token = service.create_user(db, payload)
    return Response(status_code=201, headers={config.AUTH_HEADER: token})


@router.post(config.LOGIN_URI)
async def login(
    db: Annotated[Session, Depends(get_session)], payload: UserLoginRequest
):
    token = service.get_user_token(db, payload)
    return {config.AUTH_HEADER: token}


@router.post(config.REFRESH_TOKEN_URI)
async def rotate_token(
    user: Annotated[UserEntity, Depends(service.get_user)],
    db: Annotated[Session, Depends(get_session)],
):
    new_token = service.rotate_user_token(db, user)
    return {config.AUTH_HEADER: new_token}


@router.post(config.CREATE_METRIC_URI, response_model=MetricResponse)
async def create_metric(
    user: Annotated[UserEntity, Depends(service.get_user)],
    db: Annotated[Session, Depends(get_session)],
    payload: CreateMetricRequest,
):
    return service.create_metric(db, user, payload)


@router.get(config.GET_USER_METRICS_URI, response_model=list[MetricResponse])
async def get_metrics(
    user: Annotated[UserEntity, Depends(service.get_user)],
    db: Annotated[Session, Depends(get_session)],
):
    return service.get_metrics(db, user)
