from typing import Annotated

from fastapi import Depends, HTTPException, Path, status

from app.dependencies.database import SessionDep
from app.models.room import Room

RoomId = Annotated[int, Path(ge=1, description="The ID of the room to retrieve")]


async def get_room_or_404(session: SessionDep, room_id: RoomId) -> Room:
    room = await session.get(Room, room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
        )
    return room


RoomDep = Annotated[Room, Depends(get_room_or_404)]
