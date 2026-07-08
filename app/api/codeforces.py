
from fastapi import APIRouter
from app.services.codeforces import (get_profile,get_solved_count,get_stats,get_tags,get_contest_details,get_rating_history)
from app.schemas.codeforces import(ProfileResponse,SolvedResponse,StatsResponse,TagsResponse,ContestResponse,RatingHistoryItem)

router=APIRouter()

@router.get("/{handle}", response_model=ProfileResponse)
async def profiles(handle: str):
    return await get_profile(handle)    

@router.get("/{handle}/solved", response_model=SolvedResponse)
async def solved_count(handle:str):
    return await get_solved_count(handle)

@router.get("/{handle}/stats", response_model=StatsResponse)
async def stats(handle:str):
    return await get_stats(handle)

@router.get("/{handle}/tags",response_model=TagsResponse)
async def tags(handle:str):
    return await get_tags(handle)

@router.get("/{handle}/contest",response_model=ContestResponse)
async def contest(handle:str):
    return await get_contest_details(handle)

@router.get("/{handle}/rating_history",response_model=list[RatingHistoryItem])
async def history(handle:str):
    return await get_rating_history(handle)