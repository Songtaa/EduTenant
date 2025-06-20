from typing import Tuple
from sqlalchemy import MetaData
from sqlmodel import SQLModel
from app.domains.school.models.tenant import Tenant
from app.domains.auth.models.users import User
from app.db.base_class import APIBase

import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class SchemaFactory:
    def __init__(self, schema_name: str):
        self.schema_name = schema_name
        self.source_metadata = APIBase.metadata
        self.cloned_metadata = MetaData()
        self.table_map: dict[str, object] = {}

    def clone(self) -> Tuple[MetaData, dict[str, object]]:
        """
        Clones all tenant-specific (schema-less) tables into a new MetaData
        object with schema applied and foreign keys fixed.
        """
        self._clone_schema_less_tables()
        self._attach_public_tables()
        self._fix_foreign_keys()
        
        return self.cloned_metadata, self.table_map

    def _clone_schema_less_tables(self):
        for name, table in self.source_metadata.tables.items():
            if table.schema is None:
                cloned_table = table.tometadata(self.cloned_metadata, schema=self.schema_name)
                self.table_map[name] = cloned_table
    def _fix_foreign_keys(self):
        for table in self.table_map.values():
            for fk in table.foreign_keys:
                target_name = fk.column.table.name
                if target_name in self.table_map:
                    fk.column.table = self.table_map[target_name]
                elif target_name == "users":
                    fk.column.table.schema = "public"
                elif target_name == "tenants":
                    fk.column.table.schema = "public"
                else:
                    logger.warning(f"FK target '{target_name}' not found for table '{table.name}'")



    # def _attach_public_tables(self):
    #     self.cloned_metadata._add_table("users", "public", User.__table__)
    #     self.cloned_metadata._add_table("tenants", "public", Tenant.__table__)
    #     self.cloned_metadata._add_table("tenant_permissions", "public", TenantPermission.__table__)

    def _attach_public_tables(self):
        for table in APIBase.metadata.tables.values():
            if table.schema == "public":
                self.cloned_metadata._add_table(table.name, "public", table)

