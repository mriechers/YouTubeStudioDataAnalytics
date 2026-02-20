"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, channels, videos, analytics, data


def create_app() -> FastAPI:
    app = FastAPI(
        title="PBS Wisconsin YouTube Analytics API",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3001", "http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
    app.include_router(channels.router, prefix="/api/v1", tags=["channels"])
    app.include_router(videos.router, prefix="/api/v1", tags=["videos"])
    app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
    app.include_router(data.router, prefix="/api/v1", tags=["data"])

    @app.get("/api/v1/health")
    def health_check():
        return {"status": "ok", "version": "0.1.0"}

    return app


app = create_app()
