from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.user import User
from app.services.auth import get_current_user

DBSession = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

__all__ = ["DBSession", "CurrentUser"]
