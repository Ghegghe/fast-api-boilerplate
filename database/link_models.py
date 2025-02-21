from sqlalchemy import CheckConstraint
from sqlmodel import SQLModel, Field


class PersonRelation(SQLModel, table=True):
    __tablename__: str = "person_relation"
    __table_args__ = (CheckConstraint("left_id != right_id"),)
    left_id: int | None = Field(
        foreign_key="person.id", primary_key=True, ondelete="CASCADE", default=None
    )
    right_id: int | None = Field(
        foreign_key="person.id", primary_key=True, ondelete="CASCADE", default=None
    )
