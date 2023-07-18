from datetime import timedelta, datetime
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import (
    OAuth2PasswordRequestForm,
    OAuth2PasswordBearer,
    SecurityScopes,
)
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import AuthException
from src.auth.models import User
from src.auth.schemas import (
    UserCreate,
    UserGet,
    TokenData,
    Token,
    UserScope,
    UserPermissions,
)
from src.constants import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM
from settings import settings
from src.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.ROOT_PATH}/auth/token")


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: UserCreate) -> UserGet:
        db_user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            hashed_password=pwd_context.hash(user.password),
            is_active=True,
        )
        self.session.add(db_user)
        try:
            await self.session.commit()
        except IntegrityError as err:
            raise HTTPException(
                status_code=400, detail=f"Database error: {err.orig.args[0]}"
            )
        await self.session.refresh(db_user)
        return UserGet.model_validate(db_user)

    async def get_token(self, login_form: OAuth2PasswordRequestForm) -> Token:
        user = await self._authenticate_user(login_form.username, login_form.password)
        if not user:
            raise AuthException("Incorrect username or password")
        if not user.is_active:
            raise AuthException("User isn't active")

        user_scopes = self._get_user_scopes(user)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self._create_access_token(
            data={"sub": user.email, "scopes": user_scopes},
            expires_delta=access_token_expires,
        )
        return Token(access_token=access_token, token_type="bearer")

    async def get_current_user(
        self, token: str, security_scopes: SecurityScopes
    ) -> UserPermissions:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
            if not (username := payload.get("sub")):
                raise AuthException(detail="Could not validate credentials")
            token_scopes = payload.get("scopes", [])
            token_data = TokenData(username=username, scopes=token_scopes)
        except JWTError as e:
            raise AuthException(str(e))
        if not (user := await self._get_user(token_data.username)):
            raise AuthException(detail="Could not validate credentials")
        if not set(security_scopes.scopes).intersection(set(token_data.scopes)):
            raise AuthException(
                detail="Not enough permissions",
                authenticate_value=f'Bearer scope="{security_scopes.scope_str}"',
            )
        return UserPermissions.model_validate(user)

    async def _get_user(self, login: str) -> User:
        stmt = select(User).where(User.email == login)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def _authenticate_user(self, login: str, password: str) -> User | None:
        if not (user := await self._get_user(login)):
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def _create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def _get_user_scopes(user: User) -> list[str]:
        scopes: list[str] = [UserScope.USER]
        if user.is_admin:
            scopes.append(UserScope.ADMIN)
        if user.is_superuser:
            scopes.append(UserScope.SUPERUSER)
        return scopes


async def current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_db),
) -> UserPermissions:
    service = AuthService(session)
    return await service.get_current_user(token, security_scopes)
