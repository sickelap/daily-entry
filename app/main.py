from app.api import router as api_router
from app.exceptions import EmailAlreadyExist
from fastapi import FastAPI, Response
from httpx import Request

app = FastAPI()
app.include_router(api_router)


@app.exception_handler(EmailAlreadyExist)
async def quota_exception_handler(request: Request, exc: EmailAlreadyExist):
    return Response(status_code=409)
