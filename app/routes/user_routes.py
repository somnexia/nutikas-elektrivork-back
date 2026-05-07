from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_user_service
from app.schemas.user_schema import UserReadSchema, UserUpdateSchema
from app.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserReadSchema])
async def list_users(
    limit: int = 50,
    offset: int = 0,
    user_service: UserService = Depends(get_user_service),
) -> list[UserReadSchema]:
    return await user_service.list_users(limit=limit, offset=offset)


@router.get("/{user_id}", response_model=UserReadSchema)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
) -> UserReadSchema:
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserReadSchema)
async def update_user(
    user_id: str,
    payload: UserUpdateSchema,
    user_service: UserService = Depends(get_user_service),
) -> UserReadSchema:
    user = await user_service.update_user(user_id, payload)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
) -> None:
    deleted = await user_service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return None
