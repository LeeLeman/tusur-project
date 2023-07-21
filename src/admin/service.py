from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.admin.exceptions import AdminException
from src.admin.schemas import AdminCreateUser, AdminGetUser, AdminUpdateUser
from src.auth.models import User
from src.auth.schemas import UserPermissions
from src.auth.service import pwd_context


class AdminService:
    def __init__(self, session: AsyncSession, permissions: UserPermissions):
        self.session = session
        self.permissions = permissions

    async def create_user(self, user: AdminCreateUser) -> AdminGetUser:
        if self.permissions.is_superuser:
            is_admin, is_superuser = user.is_admin, user.is_superuser
        else:
            is_admin, is_superuser = False, False
        db_user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            hashed_password=pwd_context.hash(user.password),
            is_admin=is_admin,
            is_superuser=is_superuser,
            is_active=True,
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return AdminGetUser.model_validate(db_user)

    async def update_user(self, user_id: str, user: AdminUpdateUser) -> AdminGetUser:
        res = await self.session.scalars(select(User).filter_by(user_id=user_id))
        db_user = res.first()
        user_data = user.model_dump()
        if not self.permissions.is_superuser:
            if db_user.is_admin:
                raise AdminException("Not enough permissions to update user")
            user_data.pop("is_admin")
            user_data.pop("is_superuser")
        if password := user_data.pop("password", None):
            user_data["hashed_password"] = pwd_context.hash(password)
        db_user.update(**user_data)
        await self.session.commit()
        await self.session.refresh(db_user)
        return AdminGetUser.model_validate(db_user)

    async def delete_user(self, user_id: str) -> str:
        res = await self.session.scalars(select(User).filter_by(user_id=user_id))
        db_user = res.first()
        if not self.permissions.is_superuser:
            if db_user.is_admin:
                raise AdminException("Not enough permissions to delete user")
        db_user.is_active = False
        await self.session.commit()
        return user_id
