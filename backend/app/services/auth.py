from __future__ import annotations

from fastapi import HTTPException, status

from app.models.user import User


async def get_current_user() -> User:
    user = User(id=1, email="demo@example.com", full_name="Demo User")
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user
