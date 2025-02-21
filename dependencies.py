from typing import Sequence, TypeVar, Union
from fastapi import HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Session, select, func
from database.base_models import BaseModelId
from database.engine import engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql._typing import _ColumnExpressionArgument


T = TypeVar("T", bound=BaseModelId)


class BaseFilterParams(BaseModel):
    skip: int | None = Query(
        default=None, ge=0, description="Numero di elementi da saltare"
    )
    limit: int | None = Query(
        default=None, ge=0, description="Numero massimo di elementi da restituire"
    )


class GetManyReturn[T](BaseModel):
    total: int
    items: Sequence[T]


def get_session():
    with Session(engine) as session:
        yield session


def post(cls: type[T], item: T, session: Session) -> JSONResponse:
    code = status.HTTP_200_OK
    if not item.id:
        item.id = None
        code = status.HTTP_201_CREATED
    else:
        item_db = session.get(cls, item.id)
        if not item_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="item not found"
            )
        item = item_db.sqlmodel_update(item.model_dump(exclude_unset=True))
    session.add(item)
    session.commit()
    session.refresh(item)
    return JSONResponse(status_code=code, content=item.model_dump(mode="json"))


def get_many(
    cls: type[T],
    base_filter: BaseFilterParams,
    session: Session,
    whereclause: list[Union[_ColumnExpressionArgument[bool], bool]] = [],
) -> GetManyReturn[T]:
    total = session.scalar(select(func.count()).select_from(cls))
    if total is None:
        total = 0
    items = session.exec(
        select(cls)
        .where(*whereclause)
        .offset(base_filter.skip)
        .limit(base_filter.limit)
    ).all()
    return GetManyReturn(total=total, items=items)


def get(cls: type[T], id: int, session: Session) -> T:
    item = session.get(cls, id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="item not found"
        )
    return item


def delete(cls: type[T], id: int, session: Session) -> T:
    item = session.get(cls, id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="item not found"
        )
    session.delete(item)
    try:
        session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="ForeignKeyViolation"
        )
    return item
