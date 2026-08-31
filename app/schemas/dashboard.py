
from pydantic import BaseModel
from datetime import datetime
from app.models import PlatformType
from app.schemas.codeforces import RatingHistoryItem

class DashboardSummary(BaseModel):
    id:int
    platform:PlatformType
    handle:str
    verified:bool
    created_at:datetime
    model_config={
        "from_attributes":True
    }

class DashboardAccountResponse(BaseModel):
    id:int
    handle:str
    rank:str | None=None
    rating:int | None=None
    max_rating:int | None=None
    first_name:str | None=None
    last_name:str | None=None
    updated_at:datetime
    contests:list[RatingHistoryItem]
    model_config={
        "from_attributes": True
    }