from fastapi import FastAPI

from app.api.v1.endpoints import health
from app.api.v1.router import api_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Themis AI",
        description="Microservicio de proyeccion de resultados electorales",
        version="0.1.0",
    )

    app.include_router(health.router)
    app.include_router(api_router, prefix=settings.api_prefix)

    return app


app = create_app()
