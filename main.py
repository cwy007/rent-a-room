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


@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    return {"Hello": "World"}
