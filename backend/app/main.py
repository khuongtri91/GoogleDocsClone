from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, documents, health
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="Google Docs Clone API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        str(frontend_origin).rstrip("/")
        for frontend_origin in settings.frontend_origins
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(documents.router)
