# app/docs/routes.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html

from app.docs.openapi_utils import generate_openapi_schema
from app.config.settings import settings  

def get_docs_router(app) -> APIRouter:
    router = APIRouter()

    @router.get("/docs", include_in_schema=False)
    async def custom_swagger_ui(request: Request):
        context = getattr(request.state, "context", None)
        if context not in {"tenant", "global"}:
            return JSONResponse(status_code=400, content={"detail": "Context not set in middleware"})

        return get_swagger_ui_html(
            openapi_url=f"/openapi.json?context={context}",
            title=f"{settings.PROJECT_NAME} - {context.title()} API",
            swagger_ui_parameters={"defaultModelsExpandDepth": -1}
        )
    
    
    @router.get("/tenant-docs", include_in_schema=False)
    async def tenant_swagger_ui(request: Request):
        request.state.context = "tenant"  
        return get_swagger_ui_html(
            openapi_url="/openapi.json?context=tenant",
            title=f"{settings.PROJECT_NAME} - Tenant API",
            swagger_ui_parameters={"defaultModelsExpandDepth": -1}
        )

    @router.get("/openapi.json", include_in_schema=False)
    async def custom_openapi(request: Request, context: str = None):
        print(f"Current routes: {[route.path for route in request.app.routes]}")
        ctx = context or getattr(request.state, "context", None)
        if ctx not in {"tenant", "global"}:
            return JSONResponse(status_code=400, content={"detail": "Invalid context"})

        schema = generate_openapi_schema(app, ctx, settings.PROJECT_NAME)
        return JSONResponse(schema)

    return router
