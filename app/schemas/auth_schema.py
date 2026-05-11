from pydantic import BaseModel, EmailStr

from app.schemas.user_schema import UserReadSchema


class TokenPayloadSchema(BaseModel):
    sub: str
    email: EmailStr
    exp: int


class AccessTokenPayloadSchema(BaseModel):
    sub: str
    email: EmailStr


class RefreshTokenPayloadSchema(BaseModel):
    sub: str
    jti: str
    exp: int


class AccessTokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResponseSchema(AccessTokenResponseSchema):
    user: UserReadSchema
