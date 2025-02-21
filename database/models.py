from typing import ClassVar
from sqlmodel import Relationship
from database.utisl import _SelfReferencialManyToMany, SelfReferencialManyToMany
from .base_models import (
    PersonBase,
    UserBase,
    VehicleBase,
)
from . import link_models  # always import link models first


class User(UserBase, table=True):
    pass


class Person(PersonBase, table=True):
    vehicles: list["Vehicle"] = Relationship(
        back_populates="owner", passive_deletes="all"
    )
    friends: ClassVar[_SelfReferencialManyToMany["Person"]]
    _relations_left: list["Person"] = Relationship()
    _relations_right: list["Person"] = Relationship()
    friends, _relations_left, _relations_right = SelfReferencialManyToMany["Person"](
        "Person",
        "id",
        "person_relation",
        "left_id",
        "right_id",
        "_relations_left",
        "_relations_right",
    )


class Vehicle(VehicleBase, table=True):
    owner: Person = Relationship(back_populates="vehicles", passive_deletes="all")
