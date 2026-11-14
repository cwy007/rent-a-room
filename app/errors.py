from fastapi import HTTPException, status

ROOM_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
)

USER_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
)

BOOKING_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
)

SERVICE_UNAVAILABLE = HTTPException(
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service unavailable"
)
