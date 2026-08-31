from fastapi import APIRouter
from app.services.codechef import fetch_profile,fetch_rating_history
from app.schemas.codechef import ProfileResponse,RatingHistoryItem

router=APIRouter()

@router.get("/{handle}",response_model=ProfileResponse)
async def profile(handle:str):
    return await fetch_profile(handle)

@router.get("/{handle}/rating_history",response_model=list[RatingHistoryItem])
async def history(handle:str):
    return await fetch_rating_history(handle)