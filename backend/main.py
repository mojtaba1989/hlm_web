from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from routes import lux_meter, camera_feed, recorder, logger_view
from nodes.core import core_ as core



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context: runs once on startup and once on shutdown.
    """

    yield

    cleanup(app)
    print("🧹 Cleaned up global state.")


def cleanup(app : FastAPI):
    pass

app = FastAPI(title="LHM Dashboard", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lux_meter.router, prefix="/api/lux_sensors")
app.include_router(camera_feed.router, prefix="/api/camera_feed")
app.include_router(recorder.router, prefix="/api/record")
app.include_router(logger_view.router, prefix="/api/logger")

@app.get("/")
def root():
    return {"message": "Backend is running"}