from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreateSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=8)
    username: str | None = None


class UserLoginSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: Optional[str] = Field(default=None)
    email: Optional[EmailStr] = Field(default=None)
    password: str = Field(min_length=8)


class UserUpdateSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=8)
    is_active: Optional[bool] = None


class UserReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    username: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserUnsafeReadSchema(UserReadSchema):
    password_hash: str


class UserInDBSchema(UserReadSchema):
    password_hash: str
