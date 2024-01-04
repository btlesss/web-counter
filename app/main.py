import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import frontend, api

app = FastAPI(
    title="CounterAPI",
    description="RESTful API for counting and displaying anything",
    docs_url="/api/docs",
    redoc_url="/api/docs/redoc",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(frontend.router)
app.include_router(api.router)


if __name__ == "__main__": # debug run
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )