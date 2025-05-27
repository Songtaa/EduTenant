from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional


class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str]

class RoleRead(RoleBase):
    id: UUID
    
    class Config:
        orm_mode = True
    
class RoleSchema(RoleRead):
    pass

# class PermissionCreate(BaseModel):
#     name: str

# class PermissionRead(BaseModel):
#     id: UUID
#     name: str

# class RoleWithPermissions(RoleRead):
#     permissions: List[PermissionRead] = []
