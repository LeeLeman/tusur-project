from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import UserCreate
from src.auth.service import AuthService
from src.database import get_db

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/")
async def create_user(user: UserCreate, session: AsyncSession = Depends(get_db)):
    service = AuthService(session)
    return await service.create_user(user)
