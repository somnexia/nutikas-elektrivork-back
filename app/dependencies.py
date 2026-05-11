from fastapi import Depends, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo import get_database
from app.repositories.period_repository import PeriodRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import TokenPayloadSchema
from app.services.auth_service import AuthService
from app.services.period_service import PeriodService
from app.services.user_service import UserService


def get_db() -> AsyncIOMotorDatabase:
    return get_database()


def get_user_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repository)


def get_auth_service(
    user_service: UserService = Depends(get_user_service),
) -> AuthService:
    return AuthService(user_service)




def get_period_repository(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> PeriodRepository:
    return PeriodRepository(db)

def get_period_service(
    period_repository: PeriodRepository = Depends(get_period_repository),
) -> PeriodService:
    return PeriodService(period_repository)


async def get_current_user(request: Request) -> TokenPayloadSchema:
    """Получаем пользователя из запроса"""
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user
