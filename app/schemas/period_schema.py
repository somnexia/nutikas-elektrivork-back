from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PeriodPriceItemSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    price: float
    timestamp: int


class PeriodWindowSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start: int
    end: int
    prices: list[PeriodPriceItemSchema]


class PeriodCacheSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    day: str
    periods: list[PeriodWindowSchema] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
