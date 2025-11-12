from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.database import get_session


async def get_current_user() -> User:
    """Return a demo authenticated user.

    In a real application this would validate an incoming token. For this sample
    app we simply return a static user so that dependency wiring functions.
    """

    user = User(id=1, email="demo@example.com", full_name="Demo User")
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
