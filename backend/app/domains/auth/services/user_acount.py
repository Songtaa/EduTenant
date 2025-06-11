from typing import Any, List

from db.base_class import UUID
from domains.auth.repository.user_account import users_form_actions as users_form_repo
from domains.auth.schemas.user_account import UserCreate, UserSchema, UserUpdate
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


class UserService:
    def list_users_forms(
        self, *, db: Session, skip: int = 0, limit: int = 100
    ) -> List[UserSchema]:
        users_form = users_form_repo.get_all(db=db, skip=skip, limit=limit)
        return users_form

    def create_users_forms(self, *, db: Session, users_form: UserCreate) -> UserSchema:
        users_form = users_form_repo.create(db=db, obj_in=users_form)
        return users_form

    def update_users_forms(
        self, *, db: Session, id: UUID, users_form: UserUpdate
    ) -> UserSchema:
        users_form_ = users_form_repo.get(db=db, id=id)
        if not users_form_:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="users_form not found"
            )
        users_form_ = users_form_repo.update(
            db=db, db_obj=users_form_, obj_in=users_form
        )
        return users_form_

    def get_user_by_id(self, *, db: Session, id: UUID) -> UserSchema:
        users_form = users_form_repo.get(db=db, id=id)
        if not users_form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="users_form not found"
            )
        return users_form

    def delete_users_forms(self, *, db: Session, id: UUID) -> UserSchema:
        users_form = users_form_repo.get(db=db, id=id)
        if not users_form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="users_form not found"
            )
        users_form = users_form_repo.remove(db=db, id=id)
        return users_form

    def get_users_forms_by_id(self, *, id: UUID) -> UserSchema:
        users_form = users_form_repo.get(id)
        if not users_form:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="users_form not found"
            )
        return users_form

    def get_users_forms_by_keywords(self, *, db: Session, tag: str) -> List[UserSchema]:
        pass

    def search_users_forms(
        self, *, db: Session, search: str, value: str
    ) -> List[UserSchema]:
        pass

    def read_by_kwargs(self, *, db: Session, **kwargs) -> Any:
        return users_form_repo.get_by_kwargs(self, db, kwargs)


users_forms_service = UserService()
