import re
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel, constr, EmailStr, validator

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TunedModel(BaseModel):
    class Config:
        orm_mode = True


class UserCreate(TunedModel):
    first_name: constr(min_length=1)
    last_name: constr(min_length=1)
    email: EmailStr

    @validator("first_name")
    def validate_first_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="First name should contain only letters"
            )
        return value

    @validator("last_name")
    def validate_last_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Last name should contain only letters"
            )
        return value


class User(TunedModel):
    user_id: UUID
    first_name: str
    last_name: str
    email: str
    is_active: bool

    class Config:
        orm_mode = True
