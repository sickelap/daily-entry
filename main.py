from typing import Annotated, Optional

from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI()


class AppHeaders:
    token: str


def parse_token(token: Annotated[str | None, Header()] = None) -> str | None:
    return token


@app.get("/stats")
async def get_stats(token=Depends(parse_token)):
    if not token:
        raise HTTPException(status_code=403)
    return [{"_t": 0, "v": 100.9}]
