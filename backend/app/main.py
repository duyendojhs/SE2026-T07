"""FastAPI application entrypoint."""

from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Metadata-only collaboration coach for student software teams.",
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Liveness probe used by Docker Compose and CI."""

    return {
        "status": "ok",
        "service": "github-project-coach",
        "environment": settings.app_env,
    }
