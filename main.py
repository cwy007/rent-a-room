from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.staticfiles import StaticFiles
from pydantic import AfterValidator

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

search_query_validation = Query(
    min_length=3,
    max_length=10,
    title="Search query",
    description="Search term for room names",
)


def fail_if_funny(value: str) -> str:
    if "funny" in value.lower():
        raise ValueError("Funny values are not allowed")
    return value


search_humor_ban_validation = AfterValidator(fail_if_funny)


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Welcome to the Rent a Room API"}


@app.get("/rooms", status_code=status.HTTP_200_OK)
def get_rooms(
    max_price: Annotated[int | None, Query(ge=10, le=10_000)] = None,
    search: Annotated[
        str | None,
        search_query_validation,
        search_humor_ban_validation,
    ] = None,
):
    rooms = [apartment, house, studio]
    if search:
        rooms = [room for room in rooms if search.lower() in room["name"].lower()]
    if max_price is not None:
        rooms = [room for room in rooms if room["price_per_night"] <= max_price]
    return rooms


@app.get("/rooms/mansions", status_code=status.HTTP_200_OK)
def get_mansions(
    max_price: Annotated[int | None, Query(ge=10, le=10_000)] = None,
    search: Annotated[
        str | None,
        search_query_validation,
        search_humor_ban_validation,
    ] = None,
):
    rooms = [house]
    if search:
        rooms = [room for room in rooms if search.lower() in room["name"].lower()]
    if max_price is not None:
        rooms = [room for room in rooms if room["price_per_night"] <= max_price]
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
