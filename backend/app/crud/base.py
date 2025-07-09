# app/repositories/base.py
from typing import TypeVar, Generic, Optional, Any, List, Dict, Union
from uuid import UUID
from sqlmodel import Session, SQLModel, select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
import sys
from sqlalchemy.ext.asyncio.session import AsyncSession
from pydantic import BaseModel
from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        """
        Base repository with CRUD operations
        Args:
            model: SQLModel class
            session: SQLAlchemy Session
        """
        self.model = model
        self.session = session

    async def get(self, id: Any) -> Optional[ModelType]:
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalars().first()

    def get_all(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.session.exec(
            select(self.model).offset(skip).limit(limit)
        ).all()

   

    async def create(self, obj_in: Union[CreateSchemaType, dict]) -> ModelType:
        try:
            if isinstance(obj_in, dict):
                obj_data = obj_in
            else:
                obj_data = obj_in.model_dump()

            db_obj = self.model(**obj_data)
            self.session.add(db_obj)
            await self.session.commit()
            await self.session.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await self.session.rollback()
            raise HTTPException(status_code=409, detail=str(e))
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"{type(e).__name__}: {str(e)}"
            )


    async def update(
        self, 
        *, 
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    # async def delete(self, id: Any) -> bool:
    #     db_obj = self.get(id)
    #     if db_obj:
    #         self.session.delete(db_obj)
    #         self.session.commit()
    #         return True
    #     return False


    async def delete(self, id: Any) -> bool:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        db_obj = result.scalars().first()

        if db_obj:
            await self.session.delete(db_obj)
            await self.session.commit()
            return True

        return False

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def get_by_ids(self, ids: List[Any]) -> List[ModelType]:
        if not ids:
            return []
        stmt = select(self.model).where(self.model.id.in_([ids]))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    def get_by_name(self, name: str) -> Optional[ModelType]:
        return self.session.exec(
            select(self.model).where(self.model.name == name)
        ).first()

    def search(
        self,
        field: str = None,
        value: str = None,
        case_sensitive: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Generic search with LIKE/ILIKE filtering
        Args:
            field: Column name to search in
            value: Value to search for
            case_sensitive: Use LIKE (True) or ILIKE (False)
            skip: Pagination offset
            limit: Pagination limit
        """
        query = select(self.model)
        
        if field and value:
            try:
                column = getattr(self.model, field)
                if case_sensitive:
                    query = query.where(column.like(f"%{value}%"))
                else:
                    query = query.where(column.ilike(f"%{value}%"))
            except AttributeError:
                pass  # Ignore invalid field names
        
        return self.session.exec(
            query.offset(skip).limit(limit)
        ).all()

    # Alias methods for backward compatibility
    async def read(self, *args, **kwargs):
        return self.search(*args, **kwargs)

    async def iread(self, *args, **kwargs):
        return self.search(*args, case_sensitive=False, **kwargs)

    async def read_by_id(self, id: Any):
        return self.get(id)