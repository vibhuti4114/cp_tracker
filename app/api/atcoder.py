from fastapi import APIRouter
from app.services.atcoder import fetch_profile,fetch_solved_count,fetch_rating_history
from app.schemas.atcoder import ProfileResponse,SolvedResponse,ContestResponse

router=APIRouter()

@router.get("/{handle}",response_model=ProfileResponse)
async def profile(handle:str):
    return await fetch_profile(handle)

@router.get("/{handle}/solved",response_model=SolvedResponse)
async def solved(handle:str):
    return await fetch_solved_count(handle)

@router.get("/{handle}/contest",response_model=ContestResponse)
async def contest(handle:str):
    history=await fetch_rating_history(handle)
    return{"history":history}