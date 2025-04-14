# app/docs/openapi_utils.py
from fastapi.openapi.utils import get_openapi
from typing import Any, Dict

openapi_schema_cache: Dict[str, Any] = {}

def filter_openapi_schema(schema: dict, context: str) -> dict:
    allowed_tags = {
        "global": {"Auth", "Tenants"},
        "tenant": {"Users", "Roles", "Permissions", "Services", "School"}
    }.get(context, set())

    filtered_paths = {}
    for path, methods in schema.get("paths", {}).items():
        filtered_methods = {
            method: details
            for method, details in methods.items()
            if any(tag in allowed_tags for tag in details.get("tags", []))
        }
        if filtered_methods:
            filtered_paths[path] = filtered_methods

    return {
        **schema,
        "paths": filtered_paths,
        "tags": [tag for tag in schema.get("tags", []) if tag["name"] in allowed_tags]
    }

def generate_openapi_schema(app, context: str, title: str) -> dict:
    if context not in openapi_schema_cache:
        base_schema = get_openapi(
            title=f"{title} - {context.title()} API",
            version="1.0.0",
            routes=app.routes,
        )
        openapi_schema_cache[context] = filter_openapi_schema(base_schema, context)
    return openapi_schema_cache[context]
