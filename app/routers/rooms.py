from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from pydantic import BaseModel, Field, StringConstraints, field_validator
from sqlmodel import col, select

from app.dependencies.database import SessionDep
from app.dependencies.rooms import RoomDep
from app.models.room import Room, RoomBase, RoomPublic, RoomUpdate

router = APIRouter(prefix="/rooms", tags=["rooms"])


class RoomQueryParams(BaseModel):
    max_price: int | None = Field(default=None, ge=10, le=10_000, examples=[1000, 5000])
    search: Annotated[str | None, StringConstraints(to_lower=True)] = Field(
        default=None,
        min_length=3,
        max_length=10,
        title="Search query",
        description="Search term for room names",
        examples=["cozy", "modern"],
    )
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

    @field_validator("search")
    @classmethod
    def validate_search(cls, value: str) -> str:
        if value and "funny" in value.lower():
            raise ValueError("Funny values are not allowed")
        return value


MAINTENANCE_MODE = False


def check_maintenance_mode():
    if MAINTENANCE_MODE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is under maintenance, try again later",
        )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=RoomPublic,
    dependencies=[Depends(check_maintenance_mode)],
)
async def create_room(
    session: SessionDep,
    room: RoomBase,
):
    validated_room = Room.model_validate(room)
    session.add(validated_room)
    await session.commit()
    await session.refresh(validated_room)
    return validated_room


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[RoomPublic],
    summary="summary - 获取所有房间",
    description="获取所有可用房间",
    response_description="List of rooms",
)
async def get_rooms(session: SessionDep, params: Annotated[RoomQueryParams, Query()]):
    statement = select(Room)

    if params.max_price:
        statement = statement.where(Room.price_per_night <= params.max_price)

    if params.search:
        # statement = statement.where(func.lower(Room.name).contains(params.search))
        statement = statement.where(col(Room.name).ilike(f"%{params.search}%"))

    statement = statement.limit(params.limit).offset(params.offset).order_by(Room.id)
    result = await session.exec(statement)
    return result.all()


@router.get(
    "/{room_id}",
    status_code=status.HTTP_200_OK,
    response_model=RoomPublic,
)
async def get_room(room: RoomDep):
    return room


@router.patch(
    "/{room_id}",
    status_code=status.HTTP_200_OK,
    response_model=RoomPublic,
    dependencies=[Depends(check_maintenance_mode)],
)
async def update_room(session: SessionDep, room: RoomDep, room_payload: RoomUpdate):
    room_payload_data = room_payload.model_dump(exclude_unset=True)
    room.sqlmodel_update(room_payload_data)
    session.add(room)
    await session.commit()
    await session.refresh(room)
    return room


@router.delete(
    "/{room_id}",
    status_code=status.HTTP_200_OK,
    response_model=RoomPublic,
    dependencies=[Depends(check_maintenance_mode)],
)
async def delete_room(session: SessionDep, room: RoomDep):
    session.delete(room)
    await session.commit()
    return room
