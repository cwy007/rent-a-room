from contextlib import asynccontextmanager
from typing import Annotated, Literal

from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Query,
    Response,
    status,
)
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, StringConstraints, field_validator
from sqlmodel import select

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

    @field_validator("search")
    @classmethod
    def validate_search(cls, value: str) -> str:
        if value and "funny" in value.lower():
            raise ValueError("Funny values are not allowed")
        return value


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
    rooms = session.exec(select(Room)).all()
    if params.search:
        rooms = [room for room in rooms if params.search in room.name.lower()]
    if params.max_price is not None:
        rooms = [room for room in rooms if room.price_per_night <= params.max_price]
    return rooms


@app.get(
    "/rooms/mansions",
    status_code=status.HTTP_200_OK,
    tags=["rooms"],
    deprecated=True,
)
def get_mansions(session: SessionDep, params: Annotated[RoomQueryParams, Query()]):
    rooms = session.exec(select(Room).where(Room.type == "house")).all()
    if params.search:
        rooms = [room for room in rooms if params.search in room.name.lower()]
    if params.max_price is not None:
        rooms = [room for room in rooms if room.price_per_night <= params.max_price]
    return rooms


@app.get("/rooms/faq", status_code=status.HTTP_200_OK, tags=["rooms"])
def get_rooms_faq():
    return {
        "faq": [
            {
                "question": "How do I book a room?",
                "answer": "You can book a room by selecting it and following the booking process.",
            },
            {
                "question": "What is the cancellation policy?",
                "answer": "You can cancel your booking up to 24 hours before check-in for a full refund.",
            },
        ]
    }


@app.get("/rooms/{room_id}", status_code=status.HTTP_200_OK, tags=["rooms"])
def get_room(room_id: int, session: SessionDep):
    room = session.get(Room, room_id)
    if room:
        return room
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")


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
