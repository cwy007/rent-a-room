from fastapi import APIRouter, status
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.dependencies.database import SessionDep
from app.dependencies.users import UserDep, UserId
from app.errors import USER_NOT_FOUND
from app.models.booking import BookingPublic
from app.models.user import User, UserBase, UserPublic

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
async def create_user(session: SessionDep, user: UserBase):
    new_user = User.model_validate(user)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[UserPublic])
async def get_users(session: SessionDep):
    users = await session.exec(select(User))
    return users.all()


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserPublic)
async def get_user(user: UserDep):
    return user


@router.get(
    "/{user_id}/bookings",
    status_code=status.HTTP_200_OK,
    response_model=list[BookingPublic],
)
async def get_user_bookings(session: SessionDep, user_id: UserId):
    user = await session.get(User, user_id, options=[selectinload(User.bookings)])
    if not user:
        raise USER_NOT_FOUND
    return user.bookings
