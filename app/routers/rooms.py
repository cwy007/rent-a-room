from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
)
from pydantic import BaseModel, Field, StringConstraints, field_validator
from sqlmodel import col, select

from app.dependencies.database import SessionDep
from app.models.room import Room, RoomBase, RoomPublic, RoomUpdate

router = APIRouter()


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


RoomId = Annotated[int, Path(ge=1, description="The ID of the room to retrieve")]


def get_room_or_404(session: SessionDep, room_id: RoomId) -> Room:
    room = session.get(Room, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
        )
    return room


RoomDep = Annotated[Room, Depends(get_room_or_404)]


@router.post(
    "/rooms",
    status_code=status.HTTP_201_CREATED,
    tags=["rooms"],
    response_model=RoomPublic,
)
def create_room(session: SessionDep, room: RoomBase) -> RoomPublic:
    validated_room = Room.model_validate(room)
    session.add(validated_room)
    session.commit()
    session.refresh(validated_room)
    return validated_room


@router.get(
    "/rooms",
    status_code=status.HTTP_200_OK,
    response_model=list[RoomPublic],
    tags=["rooms"],
    summary="summary - 获取所有房间",
    description="获取所有可用房间",
    response_description="List of rooms",
)
def get_rooms(session: SessionDep, params: Annotated[RoomQueryParams, Query()]):
    statement = select(Room)

    if params.max_price:
        statement = statement.where(Room.price_per_night <= params.max_price)

    if params.search:
        # statement = statement.where(func.lower(Room.name).contains(params.search))
        statement = statement.where(col(Room.name).ilike(f"%{params.search}%"))

    statement = statement.limit(params.limit).offset(params.offset).order_by(Room.id)

    return session.exec(statement).all()


@router.get(
    "/rooms/{room_id}",
    status_code=status.HTTP_200_OK,
    response_model=RoomPublic,
    tags=["rooms"],
)
def get_room(room: RoomDep):
    return room


@router.patch(
    "/rooms/{room_id}",
    status_code=status.HTTP_200_OK,
    response_model=RoomPublic,
    tags=["rooms"],
)
def update_room(session: SessionDep, room: RoomDep, room_payload: RoomUpdate):
    room_payload_data = room_payload.model_dump(exclude_unset=True)
    room.sqlmodel_update(room_payload_data)
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


@router.delete(
    "/rooms/{room_id}",
    status_code=status.HTTP_200_OK,
    response_model=RoomPublic,
    tags=["rooms"],
)
def delete_room(session: SessionDep, room: RoomDep):
    session.delete(room)
    session.commit()
    return room
