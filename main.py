from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.dependencies.database import create_db_and_tables
from app.routers import bookings, general, rooms

openapi_tags = [
    {
        "name": "rooms",
        "description": "Operations related to rooms",
    },
    {
        "name": "bookings",
        "description": "Operations related to bookings",
    },
]


def log_request(request: Request):
    print(f"{request.method} / {request.url.path}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动前
    await create_db_and_tables()
    yield
    # 关闭后


app = FastAPI(
    lifespan=lifespan,
    dependencies=[Depends(log_request)],  # 全局依赖
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
app.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
app.include_router(bookings.router)
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
