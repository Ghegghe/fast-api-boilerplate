from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session
from bearer import user_rights
from database.base_models import VehicleBase
from database.enum import VehicleBrand
from database.models import Vehicle
from dependencies import (
    BaseFilterParams,
    GetManyReturn,
    delete,
    get,
    get_many,
    get_session,
    post,
)

router = APIRouter(prefix="/vehicle", tags=["vehicle"])


class GetManyVehicleFilters(BaseModel):
    brand: VehicleBrand | None = None


@router.post(
    "",
    response_model=VehicleBase,
    dependencies=[Depends(user_rights)],
)
def post_vehicle(vehicle: Vehicle, session: Annotated[Session, Depends(get_session)]):
    return post(Vehicle, vehicle, session)


@router.get("", response_model=GetManyReturn[VehicleBase])
def get_many_vehicle(
    base_filter: Annotated[BaseFilterParams, Depends()],
    filter: Annotated[GetManyVehicleFilters, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    filters = []
    if filter.brand is not None:
        filters.append(Vehicle.brand == filter.brand)

    return get_many(Vehicle, base_filter, session, filters)


@router.get("/{vehicle_id}", response_model=VehicleBase)
def get_vehicle(vehicle_id: int, session: Annotated[Session, Depends(get_session)]):
    return get(Vehicle, vehicle_id, session)


@router.delete(
    "/{vehicle_id}",
    response_model=VehicleBase,
    dependencies=[Depends(user_rights)],
)
def delete_vehicle(vehicle_id: int, session: Annotated[Session, Depends(get_session)]):
    return delete(Vehicle, vehicle_id, session)
