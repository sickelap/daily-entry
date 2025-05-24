from typing import Annotated, Optional

from app.model import User
from app.service import get_user
from fastapi import Depends, FastAPI, HTTPException

app = FastAPI()


@app.get("/stats")
async def get_stats(user: Annotated[Optional[User], Depends(get_user)]):
    if not user:
        raise HTTPException(status_code=403)
    return user
