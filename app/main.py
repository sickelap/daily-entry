from typing import Annotated, List

from app.db import get_db
from app.model import StatAddRequest, StatImportEntry, User
from app.service import add_user_stat, get_user, import_user_stats
from fastapi import Body, Depends, FastAPI
from sqlalchemy import Engine

app = FastAPI()


@app.get("/stats")
async def get_stats(user: Annotated[User, Depends(get_user)]):
    return user


@app.post("/stats")
async def add_stat(
    user: Annotated[User, Depends(get_user)],
    db: Annotated[Engine, Depends(get_db)],
    payload: StatAddRequest,
):
    return add_user_stat(db, user, payload)


@app.post("/import")
async def import_stats(
    user: Annotated[User, Depends(get_user)],
    db: Annotated[Engine, Depends(get_db)],
    payload: Annotated[List[StatImportEntry], Body()],
):
    return import_user_stats(db, user, payload)
