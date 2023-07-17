import re
from enum import Enum

from fastapi import HTTPException
from pydantic import EmailStr, field_validator

from src.schemas import TunedModel

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class UserScope(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERUSER = "superuser"


SUPERUSER_SCOPE = [UserScope.SUPERUSER]
ADMIN_SCOPE = [UserScope.ADMIN, UserScope.SUPERUSER]


class UserBase(TunedModel):
    first_name: str
    last_name: str

    @field_validator("first_name")
    def validate_first_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value) or len(value) < 1:
            raise HTTPException(
                status_code=422, detail="First name should contain only letters"
            )
        return value

    @field_validator("last_name")
    def validate_last_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value) or len(value) < 1:
            raise HTTPException(
                status_code=422, detail="Last name should contain only letters"
            )
        return value


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserGet(UserBase):
    email: EmailStr
    is_active: bool


class UserPermissions(TunedModel):
    is_admin: bool = False
    is_superuser: bool = False


class Token(TunedModel):
    access_token: str
    token_type: str


class TokenData(TunedModel):
    username: str
    scopes: list[UserScope] = []
