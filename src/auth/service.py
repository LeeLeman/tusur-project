from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import models
from src.auth.models import User
from src.auth.schemas import UserCreate


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: UserCreate) -> User:
        db_user = models.User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            is_active=True,
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user
