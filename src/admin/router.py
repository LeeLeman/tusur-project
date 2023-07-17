from typing import Annotated

from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

from src.admin.schemas import AdminCreateUser, AdminGetUser, AdminUpdateUser
from src.admin.service import AdminService
from src.auth.schemas import UserPermissions, ADMIN_SCOPE
from src.auth.service import current_user
from src.database import get_db

admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.post("/create-user", response_model=AdminGetUser)
async def create_user(
    permissions: Annotated[UserPermissions, Security(current_user, scopes=ADMIN_SCOPE)],
    user_data: AdminCreateUser,
    session: AsyncSession = Depends(get_db),
):
    service = AdminService(session, permissions)
    return await service.create_user(user_data)


@admin_router.put("/update-user", response_model=AdminGetUser)
async def update_user(
    permissions: Annotated[UserPermissions, Security(current_user, scopes=ADMIN_SCOPE)],
    user_id: str,
    user_data: AdminUpdateUser,
    session: AsyncSession = Depends(get_db),
):
    service = AdminService(session, permissions)
    return await service.update_user(user_id, user_data)


@admin_router.delete("/delete-user")
async def delete_user(
    permissions: Annotated[UserPermissions, Security(current_user, scopes=ADMIN_SCOPE)],
    user_id: str,
    session: AsyncSession = Depends(get_db),
):
    service = AdminService(session, permissions)
    res = await service.delete_user(user_id)
    return {"status": f"user_id {res} was deleted"}
