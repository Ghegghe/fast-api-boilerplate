from typing import Annotated
from fastapi import APIRouter, Depends
from sqlmodel import Session
from bearer import get_user_from_token, oauth2_scheme, UserResponse
from database.models import User
from dependencies import (
    BaseFilterParams,
    GetManyReturn,
    delete,
    get,
    get_many,
    get_session,
)


router = APIRouter(prefix="/user", tags=["user"])


@router.get("", response_model=GetManyReturn[UserResponse])
def get_many_user(
    base_filter: Annotated[BaseFilterParams, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    return get_many(User, base_filter, session)


@router.get("/me", response_model=UserResponse)
def get_user_me(
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
):
    return get_user_from_token(session, token)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: Annotated[Session, Depends(get_session)]):
    return get(User, user_id, session)


@router.delete("/{user_id}", response_model=UserResponse)
def delete_user(user_id: int, session: Annotated[Session, Depends(get_session)]):
    return delete(User, user_id, session)
