from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.dependencies.database import create_db_and_tables
from app.routers import general, rooms

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
app.include_router(general.router)
app.include_router(rooms.router)
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
