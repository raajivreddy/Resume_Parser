from fastapi import FastAPI
from app.api.routes import router as api_router
from app.utils.config import settings
from app.utils.logger import logger

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Production-ready Resume Parser API using Transformer Models"
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.on_event("startup")
    async def startup_event():
        logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    return app

app = create_app()
