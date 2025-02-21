from __future__ import annotations
from sqlalchemy.orm import relationship
from typing import Any, Callable, Generator, Generic, TypeVar
from operator import lt
from sqlmodel import Relationship

_T = TypeVar("_T")
_V = TypeVar("_V")


class _SelfReferencialManyToMany(Generic[_T]):
    def __init__(
        self,
        key: str,
        adjacencies_1_name: str,
        adjacencies_2_name: str,
        compare: Callable = lt,
    ):
        self.key = key
        self.adjacencies_1 = adjacencies_1_name
        self.adjacencies_2 = adjacencies_2_name
        self.compare = compare

    def __set_name__(self, _, name: str):
        key = self.key
        adjacencies_1 = self.adjacencies_1
        adjacencies_2 = self.adjacencies_2
        compare = self.compare

        class Proxy(Generic[_V]):
            def __init__(self, obj: _V):
                self.obj = obj

            __emulates__ = list

            def __repr__(self):
                return repr(list(self.__iter__()))

            def _compare(self, other: _V) -> bool:
                val = getattr(self.obj, key)
                comp_val = getattr(other, key)
                if val is None:
                    return False
                elif comp_val is None:
                    return True
                return compare(getattr(self.obj, key), comp_val)

            def append(self, other: _V) -> None:
                if self._compare(other):
                    getattr(self.obj, adjacencies_1).append(other)
                else:
                    getattr(self.obj, adjacencies_2).append(other)

            def remove(self, other: _V) -> None:
                if self._compare(other):
                    getattr(self.obj, adjacencies_1).remove(other)
                else:
                    getattr(self.obj, adjacencies_2).remove(other)

            def extend(self, others: list[_V]) -> None:
                others_1 = []
                others_2 = []
                for other in others:
                    if self._compare(other):
                        others_1.append(other)
                    else:
                        others_2.append(other)
                getattr(self.obj, adjacencies_1).extend(others_1)
                getattr(self.obj, adjacencies_2).extend(others_2)

            def __iter__(self) -> Generator[_V, Any, Any]:
                yield from getattr(self.obj, adjacencies_1)
                yield from getattr(self.obj, adjacencies_2)

            def __next__(self) -> Generator[_V, Any, Any]:
                yield from getattr(self.obj, adjacencies_1)
                yield from getattr(self.obj, adjacencies_2)

        self.Proxy = Proxy[_T]

    def __get__(self, obj, _):
        return self.Proxy(obj)


class SelfReferencialManyToMany(Generic[_T]):
    def __new__(
        cls,
        cls_name: str,
        cls_key: str,
        link_cls: str,
        link_cls_key_1: str,
        link_cls_key_2: str,
        cls_relation_name_1: str,
        cls_relation_name_2: str,
    ) -> tuple[_SelfReferencialManyToMany[_T], list[_T], list[_T]]:
        half_adjacency_1 = Relationship(
            sa_relationship=relationship(
                argument=cls_name,
                secondary=link_cls,
                primaryjoin=f"{cls_name}.{cls_key} == {link_cls}.c.{link_cls_key_1}",
                secondaryjoin=f"{cls_name}.{cls_key} == {link_cls}.c.{link_cls_key_2}",
                back_populates=cls_relation_name_2,
            ),
        )
        half_adjacency_2 = Relationship(
            sa_relationship=relationship(
                argument=cls_name,
                secondary=link_cls,
                primaryjoin=f"{cls_name}.{cls_key} == {link_cls}.c.{link_cls_key_2}",
                secondaryjoin=f"{cls_name}.{cls_key} == {link_cls}.c.{link_cls_key_1}",
                back_populates=cls_relation_name_1,
            ),
        )
        full_adjacency = _SelfReferencialManyToMany[_T](
            cls_key, cls_relation_name_1, cls_relation_name_2
        )
        return full_adjacency, half_adjacency_1, half_adjacency_2
