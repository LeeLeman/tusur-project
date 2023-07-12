import re

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, field_validator

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TunedModel(BaseModel):
    class Config:
        from_attributes = True


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


class Token(TunedModel):
    access_token: str
    token_type: str


class TokenData(TunedModel):
    username: str | None = None
