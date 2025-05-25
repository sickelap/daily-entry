from app import exceptions
from app.api import router as api_router
from fastapi import FastAPI, Response
from httpx import Request

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.include_router(api_router)


@app.exception_handler(exceptions.EmailAlreadyExist)
async def email_already_exist(request: Request, exc: exceptions.EmailAlreadyExist):
    return Response(status_code=409)


@app.exception_handler(exceptions.Unauthorized)
async def invalid_credentials(request: Request, exc: exceptions.Unauthorized):
    return Response(status_code=401)
