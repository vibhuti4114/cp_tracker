
from fastapi import APIRouter,Depends
from app.services.codeforces import (fetch_profile,fetch_solved_count,fetch_tags,build_contest_stats,fetch_rating_history)
from app.schemas.codeforces import(ProfileResponse,SolvedResponse,TagsResponse,ContestResponse,RatingHistoryItem)
from app.database.dependencies import get_db
from sqlalchemy.orm import Session

router=APIRouter()

@router.get("/{handle}", response_model=ProfileResponse)
async def profile(handle: str,db:Session=Depends(get_db)):
    return await fetch_profile(handle)

@router.get("/{handle}/solved", response_model=SolvedResponse)
async def solved_count(handle:str):
    return await fetch_solved_count(handle)

@router.get("/{handle}/tags",response_model=TagsResponse)
async def tags(handle:str):
    return await fetch_tags(handle)

@router.get("/{handle}/contest",response_model=ContestResponse)
async def contest(handle:str):
    return await build_contest_stats(handle)

@router.get("/{handle}/rating_history",response_model=list[RatingHistoryItem])
async def history(handle:str):
    return await fetch_rating_history(handle)