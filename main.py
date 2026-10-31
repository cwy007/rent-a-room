from contextlib import asynccontextmanager
from typing import Annotated, Literal

from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    status,
)
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, StringConstraints, field_validator
from sqlmodel import col, func, or_, select

from database import SessionDep, create_db_and_tables
from models import Room

openapi_tags = [
    {
        "name": "rooms",
        "description": "Operations related to rooms",
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动前
    create_db_and_tables()
    yield
    # 关闭后


app = FastAPI(
    lifespan=lifespan,
    title="Rent a Room API",
    description="API for managing room rentals",
    version="1.0.0",
    contact={
        "name": "Support",
        "email": "support@rentaroom.com",
    },
    openapi_tags=openapi_tags,
)
app.mount("/assets", StaticFiles(directory="assets"), name="assets")


class AppCookies(BaseModel):
    theme: Literal["light", "dark"] = "dark"
    language: Literal["en", "es", "fr"] = "en"


class AppHeaders(BaseModel):
    user_agent: str | None = None


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


@app.get("/", status_code=status.HTTP_200_OK)
def root(
    app_cookies: Annotated[AppCookies, Cookie()],
    app_headers: Annotated[AppHeaders, Header()],
    session: SessionDep,
):
    db_result = session.exec(select(5)).one()

    greetings = {
        "en": "Welcome to Rent a Room",
        "es": "Bienvenido a Rent a Room",
        "fr": "Bienvenue à Rent a Room",
    }
    language = app_cookies.language
    return {
        "message": greetings.get(language),
        "language": language,
        "user_agent": app_headers.user_agent if app_headers else None,
        "app_headers": app_headers.model_dump() if app_headers else None,
        "db_result": db_result,
    }


@app.post("/rooms", status_code=status.HTTP_201_CREATED, tags=["rooms"])
def create_room(session: SessionDep, room: Room) -> Room:
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


@app.get(
    "/rooms",
    status_code=status.HTTP_200_OK,
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


@app.get("/rooms/{room_id}", status_code=status.HTTP_200_OK, tags=["rooms"])
def get_room(session: SessionDep, room_id: RoomId) -> Room:
    room = session.get(Room, room_id)
    if room:
        return room
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")


@app.patch("/rooms/{room_id}", status_code=status.HTTP_200_OK, tags=["rooms"])
def update_room(session: SessionDep, room_id: RoomId, room: Room) -> Room:
    existing_room = session.get(Room, room_id)
    if not existing_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
        )
    # for key, value in room.model_dump().items():
    #     setattr(existing_room, key, value)
    existing_room.sqlmodel_update(room)
    session.add(existing_room)
    session.commit()
    session.refresh(existing_room)
    return existing_room


@app.get("/preferences", status_code=status.HTTP_200_OK, tags=["preferences"])
def set_preferences(response: Response):
    app_cookies = AppCookies()
    response.set_cookie(key="theme", value=app_cookies.theme)
    response.set_cookie(key="language", value=app_cookies.language)
    return {"message": "Preferences updated"}


def get_number():
    return 42


@app.get("/example")
def fake_route(number: Annotated[int, Depends(get_number)]):
    return {"number": number}
