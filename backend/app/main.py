"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, health, tenants, webhooks
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Metadata-only collaboration coach for student software teams.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(tenants.router)
app.include_router(webhooks.router)
