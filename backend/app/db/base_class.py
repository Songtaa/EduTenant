from typing import Optional
import uuid
from datetime import datetime
from functools import reduce

import inflect
from sqlmodel import SQLModel, Field
from sqlalchemy.ext.declarative import declared_attr


# Function to convert CamelCase to snake_case
def change_case(str: str):
    return reduce(lambda x, y: x + ("_" if y.isupper() else "") + y, str).lower()


# Base class using SQLModel
class Base(SQLModel):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True
    )

    @declared_attr
    def __tablename__(cls) -> str:
        camel_check = change_case(cls.__name__)
        p = inflect.engine()
        return p.plural(camel_check.lower())


class APIBase(Base):  # `table=True` makes it a table model in SQLModel
    created_date: Optional[datetime] = Field(
        default_factory=datetime.now, nullable=False
    )
    updated_date: Optional[datetime] = Field(
        default_factory=datetime.now, nullable=False
    )


# import typing as t
# import uuid
# from datetime import datetime
# from functools import reduce

# import inflect
# import sqlalchemy.dialects.postgresql as pg
# from sqlalchemy import Column
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.ext.declarative import as_declarative, declared_attr

# class_registry: t.Dict = {}


# def change_case(str):
#     return reduce(lambda x, y: x + ("_" if y.isupper() else "") + y, str).lower()


# @as_declarative(class_registry=class_registry)
# class Base:
#     id: t.Any
#     __name__: str

#     # Generate __tablename__ automatically
#     @declared_attr
#     def __tablename__(cls) -> str:
#         camel_check = change_case(cls.__name__)
#         p = inflect.engine()
#         return p.plural(camel_check.lower())


# class APIBase(Base):
#     __abstract__ = True

#     id = Column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         index=True,
#         nullable=False,
#         default=uuid.uuid4,
#     )

#     created_date = Column(
#         pg.TIMESTAMP(timezone=True), default=(datetime.now), nullable=False
#     )
#     updated_date = Column(
#         pg.TIMESTAMP(timezone=True),
#         default=(datetime.now),
#         onupdate=(datetime.now),
#         nullable=False,
#     )


# import uuid
# from datetime import datetime
# from sqlmodel import SQLModel, Field
# from typing import Optional
# from sqlalchemy import func
# from sqlalchemy.orm import declared_attr


# class BaseModel(SQLModel):
#     id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
#     created_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
#     updated_date: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": func.now()})

#     @declared_attr
#     def __tablename__(cls) -> str:
#         return cls.__name__.lower()
