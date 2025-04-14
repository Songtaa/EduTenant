# app/core/tenant_dependencies.py
from fastapi import Request, HTTPException, Depends
from typing import Generator, Optional
from uuid import UUID
from app.db.session import get_tenant_session
from sqlmodel import Session
from fastapi import Request, HTTPException, status, Depends

def get_tenant_id(request: Request) -> str:
    """Extract tenant ID from request"""
    tenant_id = None
    
    # Check subdomain (school1.example.com)
    host = request.headers.get("host", "").split(".")
    if len(host) > 2 and host[0] != "www":
        tenant_id = host[0]
    
    # Fallback to header
    if not tenant_id:
        tenant_id = request.headers.get("X-Tenant-ID")
    
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant not specified")
    
    return tenant_id

def get_tenant_db(tenant_id: str = Depends(get_tenant_id)) -> Generator[Session, None, None]:
    """Dependency that returns tenant-specific database session"""
    return get_tenant_session(tenant_id)

# Shortcut for common case
get_tenant_id = Depends(get_tenant_id)
get_tenant_db = Depends(get_tenant_db)



def require_global_context(request: Request):
    if getattr(request.state, "context", None) != "global":
        raise HTTPException(status_code=403, detail="Only accessible from global context")


def require_tenant_context(request: Request):
    if getattr(request.state, "context", None) != "tenant":
        raise HTTPException(status_code=403, detail="Only accessible from tenant context")
