from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field
from .enum import (
    UserRoleEnum,
    VehicleBrand,
)


class BaseModelId(SQLModel):
    id: int | None = Field(default=None, primary_key=True, gt=0)


class UserBase(BaseModelId):
    username: str = Field(max_length=50, unique=True)
    email: str = Field(unique=True)
    password_hash: str
    role: UserRoleEnum


class PersonBase(BaseModelId):
    name: str = Field(max_length=50)
    surname: str | None = Field(default=None, max_length=50)
    birth_date: datetime | None = Field(sa_column=Column(DateTime(timezone=True)))


class VehicleBase(BaseModelId):
    name: str = Field(max_length=50)
    brand: VehicleBrand
    person_id: int = Field(foreign_key="person.id", ondelete="CASCADE", gt=0)
