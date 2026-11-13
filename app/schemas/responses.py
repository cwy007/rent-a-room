from app.models.booking import BookingPublic
from app.models.room import RoomPublic
from app.models.user import UserPublic


class BookingWithDetails(BookingPublic):
    user: UserPublic
    room: RoomPublic
