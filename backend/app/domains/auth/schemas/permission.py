from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional

class PermissionBase(BaseModel):
    name: str

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    name: Optional[str]

class PermissionRead(BaseModel):
    id: UUID
    
    class Config:
        orm_mode = True
    
class PermissionSchema(PermissionRead):
    pass



