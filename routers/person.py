from datetime import date
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlmodel import Session, col
from database.base_models import PersonBase
from database.models import Person
from dependencies import (
    BaseFilterParams,
    GetManyReturn,
    delete,
    get,
    get_many,
    get_session,
    post,
)

router = APIRouter(prefix="/person", tags=["person"])


class GetManyPersonFilters(BaseModel):
    birth_date: date | None = None
    name: Annotated[str | None, Query(description="LIKE comparation")] = None


class PostPerson(PersonBase):
    friends: list[Person] = []


@router.post("", response_model=PersonBase)
def post_person(
    person: PostPerson,
    session: Annotated[Session, Depends(get_session)],
):
    new_person = Person.model_validate(person)
    if person.friends:
        new_person.friends.extend(person.friends)
    return post(Person, new_person, session)


@router.get("", response_model=GetManyReturn[Person])
def get_many_person(
    base_filter: Annotated[BaseFilterParams, Depends()],
    filter: Annotated[GetManyPersonFilters, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    filters = []
    if filter.birth_date:
        filters.append((Person.birth_date == filter.birth_date))
    if filter.name:
        filters.append(col(Person.name).like(f"%{filter.name}%"))

    return get_many(Person, base_filter, session, filters)


@router.get("/{person_id}", response_model=PersonBase)
def get_person(person_id: int, session: Annotated[Session, Depends(get_session)]):
    return get(Person, person_id, session)


@router.delete("/{person_id}", response_model=Person)
def delete_person(person_id: int, session: Annotated[Session, Depends(get_session)]):
    return delete(Person, person_id, session)
