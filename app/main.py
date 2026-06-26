from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.routes import router as api_router
from app.utils.config import settings
from app.utils.logger import logger
from app.utils.exceptions import ResumeParserException
from app.models.schemas import ParseResponse

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

    # Global Exception Handlers
    @app.exception_handler(ResumeParserException)
    async def resume_parser_exception_handler(request: Request, exc: ResumeParserException):
        logger.warning(f"Domain Error: {exc.message}")
        response = ParseResponse(status="error", data=None, message=exc.message)
        return JSONResponse(status_code=exc.status_code, content=response.model_dump())

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled Server Error: {str(exc)}", exc_info=True)
        response = ParseResponse(status="error", data=None, message="An unexpected internal server error occurred.")
        return JSONResponse(status_code=500, content=response.model_dump())

    return app

app = create_app()
