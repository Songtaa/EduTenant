# from apis.routers import router as api_router
# from db.session import SessionLocal
# from apis.routers import routers as api_router
# from apis.routers import router as api_router
# from apis.routers import router as api_router
from contextlib import asynccontextmanager

from app.apis.routers import router as api_router
from app.config.settings import settings 
from app.db.init_db import init_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
# from starlette.middleware.cors import CORSMiddleware
from app.utils.errors import register_all_errors

# from config.settings import Settings as settings


# from app.apis.main import api_router
# from app.config import settings

# from domains.appraisal.schemas.appraisal_section import validate_appraisal_cycles_id


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


# if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
#     sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)


@asynccontextmanager
async def life_span(app: FastAPI):
    print("server is starting ...")
    await init_db()
    yield
    print("server has been stopped")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=life_span,
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

register_all_errors(app)

app.include_router(api_router, prefix=settings.API_V1_STR)
