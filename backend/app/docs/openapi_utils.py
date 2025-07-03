# app/docs/openapi_utils.py
from fastapi.openapi.utils import get_openapi
from typing import Any, Dict
from app.config.settings import settings 
import re

openapi_schema_cache: Dict[str, Any] = {}


def filter_openapi_schema(schema: dict, context: str) -> dict:
    # Define exact path patterns for each context
    context_patterns = {
        "global": [
            f"^{settings.API_V1_STR}/auth/",
            f"^{settings.API_V1_STR}/users/",
            f"^{settings.API_V1_STR}/roles/",
            f"^{settings.API_V1_STR}/permissions/",
            # f"^{settings.API_V1_STR}/tenants$",  # Only tenant management (no trailing slash)
            f"^{settings.API_V1_STR}/tenants/",  # List/Create tenants
            # f"^{settings.API_V1_STR}/tenants/[^/]+$"  # Specific tenant management
        ],
        "tenant": [
            f"^{settings.API_V1_STR}/tenants/[^/]+/services/",
            f"^{settings.API_V1_STR}/tenants/[^/]+/schools/"
        ]
    }
    
    
    filtered_paths = {}
    
    for path, methods in schema.get("paths", {}).items():
        
        if any(re.match(pattern, path) for pattern in context_patterns[context]):
            filtered_paths[path] = methods
    
    return {
        **schema,
        "paths": filtered_paths,
        "tags": [tag for tag in schema.get("tags", []) 
               if any(re.match(pattern, path)
                     for pattern in context_patterns[context]
                     for path in filtered_paths)]
    }


def generate_openapi_schema(app, context: str, title: str) -> dict:
    
    base_schema = get_openapi(
        title=f"{title} - {context.title()} API",
        version="1.0.0",
        routes=app.routes,
    )
    return filter_openapi_schema(base_schema, context)
