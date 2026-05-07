from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreateSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=8)
    username: str | None = None


class UserUpdateSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str | None = None
    password: str | None = Field(default=None, min_length=8)
    is_active: bool | None = None


class UserReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    username: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserInDBSchema(UserReadSchema):
    password_hash: str
