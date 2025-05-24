from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/stats")
async def get_stats():
    raise HTTPException(status_code=403)
