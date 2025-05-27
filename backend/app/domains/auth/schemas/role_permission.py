from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from role import RoleRead
from permission import PermissionRead

class RolePermissions(RoleRead):
    permissions: List[PermissionRead] = []

