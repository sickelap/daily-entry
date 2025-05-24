from typing import Annotated

from app.db import get_db
from app.model import StatAddRequest, User
from app.service import add_user_stat, get_user
from fastapi import Depends, FastAPI
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
