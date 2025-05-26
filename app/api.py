from typing import Annotated


from app import config
from app import db
from app.model import (
    CreateMetricRequest,
    EmailAndPassword,
    MetricEntity,
    MetricResponse,
    Tokens,
    UserEntity,
    UserRegisterRequest,
    ValueRequest,
)
from app import service
from fastapi import APIRouter, Body, Depends
from sqlmodel import Session

router = APIRouter(prefix=config.API_PREFIX)


@router.post(config.REGISTER_URI)
async def register(
    db: Annotated[Session, Depends(db.get_session)], payload: UserRegisterRequest
):
    return service.create_user(db, payload)


@router.post(config.LOGIN_URI)
async def login(
    db: Annotated[Session, Depends(db.get_session)], data: EmailAndPassword
):
    return service.login(db, data)


@router.post(config.REFRESH_TOKEN_URI)
async def refresh_token(
    token: Annotated[str, Depends(service.oauth2_scheme)],
) -> Tokens:
    return service.refresh_token(token)


@router.post(config.METRICS_URI, response_model=MetricResponse)
async def create_metric(
    user: Annotated[UserEntity, Depends(service.get_user)],
    db: Annotated[Session, Depends(db.get_session)],
    payload: CreateMetricRequest,
):
    return service.create_metric(db, user, payload)


@router.get(config.METRICS_URI, response_model=list[MetricResponse])
async def get_metrics(
    user: Annotated[UserEntity, Depends(service.get_user)],
    db: Annotated[Session, Depends(db.get_session)],
):
    return service.get_metrics(db, user)


@router.post(config.VALUES_URI)
async def add_values(
    db: Annotated[Session, Depends(db.get_session)],
    metric: Annotated[MetricEntity, Depends(service.get_metric)],
    payload: list[ValueRequest] = Body(...),
):
    return service.add_values(db, metric, payload)


@router.get(config.VALUES_URI)
async def get_values(
    db: Annotated[Session, Depends(db.get_session)],
    metric: Annotated[MetricEntity, Depends(service.get_metric)],
):
    return service.get_values(db, metric)
