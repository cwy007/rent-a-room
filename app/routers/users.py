from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.dependencies.database import SessionDep
from app.dependencies.users import UserDep, UserId
from app.models.booking import BookingPublic
from app.models.user import User, UserBase, UserPublic, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
async def create_user(session: SessionDep, user: UserBase):
    new_user = User.model_validate(user)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserPublic)
async def get_user(user: UserDep):
    return user


@router.get(
    "/{user_id}/bookings",
    status_code=status.HTTP_200_OK,
    response_model=list[BookingPublic],
)
async def get_user_bookings(user: UserDep):
    return user.bookings
