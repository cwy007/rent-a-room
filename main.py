from fastapi import FastAPI, status

app = FastAPI(
    title="Rent a Room API",
    description="API for managing room rentals",
    version="1.0.0",
    contact={
        "name": "Support",
        "email": "support@rentaroom.com",
    },
)

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


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Welcome to the Rent a Room API"}


@app.get("/rooms", status_code=status.HTTP_200_OK)
def get_rooms():
    return [apartment, house, studio]


@app.get("/rooms/{room_id}", status_code=status.HTTP_200_OK)
def read_room(room_id: int):
    for room in [apartment, house, studio]:
        if room["id"] == room_id:
            return room
    return {"error": "Room not found"}
