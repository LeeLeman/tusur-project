from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import UserCreate, UserGet, Token
from src.auth.service import AuthService
from src.database import get_db

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserGet)
async def create_user(user: UserCreate, session: AsyncSession = Depends(get_db)):
    service = AuthService(session)
    return await service.create_user(user)


@auth_router.post("/token", response_model=Token)
async def get_token(
    login_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_db),
):
    service = AuthService(session)
    return await service.get_token(login_form)
