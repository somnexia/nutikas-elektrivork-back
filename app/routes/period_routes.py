from fastapi import APIRouter, Depends

from app.dependencies import get_current_user, get_period_service
from app.schemas.auth_schema import TokenPayloadSchema
from app.schemas.period_schema import PeriodWindowSchema
from app.services.period_service import PeriodService


router = APIRouter(prefix="/periods", tags=["periods"])


@router.get("", response_model=list[PeriodWindowSchema])
async def list_periods(
    current_user: TokenPayloadSchema = Depends(get_current_user),
    period_service: PeriodService = Depends(get_period_service),
) -> list[PeriodWindowSchema]:
    return await period_service.get_periods(current_user.sub)
