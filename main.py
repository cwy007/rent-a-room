from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, StringConstraints, field_validator

app = FastAPI(
    title="Rent a Room API",
    description="API for managing room rentals",
    version="1.0.0",
    contact={
        "name": "Support",
        "email": "support@rentaroom.com",
    },
)
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

apartment = {
    "id": 1,
    "name": "Cozy Apartment",
    "price_per_night": 1200,
    "bedrooms": 2,
    "bathrooms": 1,
}

house = {
    "id": 2,
    "name": "Spacious House",
    "price_per_night": 2500,
    "bedrooms": 4,
    "bathrooms": 3,
}

studio = {
    "id": 3,
    "name": "Modern Studio",
    "price_per_night": 900,
    "bedrooms": 1,
    "bathrooms": 1,
}


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
def root():
    return {"message": "Welcome to the Rent a Room API"}


@app.get("/rooms", status_code=status.HTTP_200_OK)
def get_rooms(params: Annotated[RoomQueryParams, Query()]):
    rooms = [apartment, house, studio]
    if params.search:
        rooms = [room for room in rooms if params.search in room["name"].lower()]
    if params.max_price is not None:
        rooms = [room for room in rooms if room["price_per_night"] <= params.max_price]
    return rooms


@app.get("/rooms/mansions", status_code=status.HTTP_200_OK)
def get_mansions(params: Annotated[RoomQueryParams, Query()]):
    rooms = [house]
    if params.search:
        rooms = [room for room in rooms if params.search in room["name"].lower()]
    if params.max_price is not None:
        rooms = [room for room in rooms if room["price_per_night"] <= params.max_price]
    return rooms


@app.get("/rooms/faq", status_code=status.HTTP_200_OK)
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


@app.get("/rooms/{room_id}", status_code=status.HTTP_200_OK)
def get_room(room_id: int):
    for room in [apartment, house, studio]:
        if room["id"] == room_id:
            return room
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
