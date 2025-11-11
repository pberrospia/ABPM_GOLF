from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.core.config import settings
from app.core.dependencies import CurrentUser, DBSession
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models import User
from app.schemas.auth import Token, UserCreate, UserRead
from app.utils.files import sanitize_upload_filename

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, session: DBSession) -> UserRead:
    result = await session.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserRead.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: DBSession,
) -> Token:
    result = await session.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    token = create_access_token(user.email)
    return Token(access_token=token)


@router.post("/signature", response_model=UserRead)
async def upload_signature(
    file: UploadFile,
    current_user: CurrentUser,
    session: DBSession,
) -> UserRead:
    sanitized_name = sanitize_upload_filename(file.filename, fallback="signature")
    filename = f"signature_{current_user.id}_{sanitized_name}"
    path = settings.storage_dir / filename
    content = await file.read()
    path.write_bytes(content)

    current_user.signature_path = str(path)
    current_user.updated_at = datetime.utcnow()
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return UserRead.model_validate(current_user)
