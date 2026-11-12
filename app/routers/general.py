from typing import Annotated, Literal

from fastapi import APIRouter, Cookie, Depends, Header, Response, status
from pydantic import BaseModel
from sqlmodel import select

from app.dependencies.database import SessionDep

router = APIRouter()


class AppCookies(BaseModel):
    theme: Literal["light", "dark"] = "dark"
    language: Literal["en", "es", "fr"] = "en"


class AppHeaders(BaseModel):
    user_agent: str | None = None


@router.get("/", status_code=status.HTTP_200_OK)
async def root(
    app_cookies: Annotated[AppCookies, Cookie()],
    app_headers: Annotated[AppHeaders, Header()],
    session: SessionDep,
):
    db_result = await session.exec(select(5))
    db_result = db_result.one()

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


@router.get("/preferences", status_code=status.HTTP_200_OK, tags=["preferences"])
def set_preferences(response: Response):
    app_cookies = AppCookies()
    response.set_cookie(key="theme", value=app_cookies.theme)
    response.set_cookie(key="language", value=app_cookies.language)
    return {"message": "Preferences updated"}


def get_number():
    return 42


@router.get("/example")
def fake_route(number: Annotated[int, Depends(get_number)]):
    return {"number": number}
