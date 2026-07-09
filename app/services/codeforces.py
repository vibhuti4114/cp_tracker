
import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.cf_profile import get_cached_profile,create_catched_profile

BASE_URL = "https://codeforces.com/api"

# ----------------------------------------------------------------------------------------------------
# Helper Function
# ----------------------------------------------------------------------------------------------------

async def get_submissions(handle: str):
    url = f"{BASE_URL}/user.status?handle={handle}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)

    data = response.json()
    if data["status"] != "OK":
        raise HTTPException(
            status_code=404,
            detail="Handle not found"
        )

    return data["result"]

async def get_unique_solved(handle:str):
    submission=await get_submissions(handle)
    solved={}

    for sub in submission:
        if sub["verdict"]=="OK":
            problem=sub["problem"]
            key=(
                problem.get("contestId"),
                problem.get("index")
            )
            solved[key]=problem

    return solved

async def get_contests(handle:str):
    url=f"{BASE_URL}/user.rating?handle={handle}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response=await client.get(url)

    data=response.json()
    if data["status"] !="OK":
        raise HTTPException(
            status_code=404,
            detail="Handle not found"
        )
    contest=data["result"]

    return contest

# ----------------------------------------------------------------------------------------------------
# Services
# ----------------------------------------------------------------------------------------------------

async def get_profile(handle :str,db:Session):
    cached=get_cached_profile(db,handle)
    if(cached):
        print("Return From Database",cached.handle)
        return{
            "handle": cached.handle,
            "rating": cached.rating,
            "max_rating": cached.max_rating,
            "rank": cached.rank
        }
    print("Fetched From codeforces")
    url=f"{BASE_URL}/user.info?handles={handle}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response=await client.get(url)

    data=response.json()

    if data["status"]!="OK":
        raise HTTPException(
            status_code=404,
            detail="Handle not found"
        )
    
    user=data["result"][0]
    profile_details={
        "handle": user["handle"],
        "rating": user.get("rating"),
        "max_rating": user.get("maxRating"),
        "rank": user.get("rank"),
    }
    create_catched_profile(db,profile_details)

    return profile_details

async def get_solved_count(handle :str):
    solved=await get_unique_solved(handle)

    return {
        "handle": handle,
        "problems_solved": len(solved)
    }

async def get_stats(handle:str):
    solved=await get_unique_solved(handle)
    ratings=[]

    for problem in solved.values():
        if "rating" in problem:
            ratings.append(problem["rating"])
    
    max_rating_solved=None
    avg_rating_solved=None

    if ratings:
        avg_rating_solved=round(sum(ratings)/len(ratings))
        max_rating_solved=max(ratings)

    return {
        "handle": handle,
        "problems_solved": len(solved),
        "average_rating_solved": avg_rating_solved,
        "max_rating_solved": max_rating_solved
    }


async def get_tags(handle:str):
    solved=await get_unique_solved(handle)
    tag={}

    for problem in solved.values():
        for t in problem.get("tags",[]):
            tag[t]=tag.get(t,0)+1
    
    tag=dict(
        sorted(
            tag.items(),
            key=lambda x:x[1],
            reverse=True
        )
    )
    
    return{
        "handle":handle,
        "tags":tag
    }


async def get_contest_details(handle:str):
    contests=await get_contests(handle)

    if not contests:
        return{
            "handle":handle,
            "contest_attended":len(contests),
            "best_rank":None,
            "worst_rank":None,
            "max_rating":None,
            "current_rating":None
        }
    
    rating=[c["newRating"] for c in contests]
    rank=[c["rank"] for c in contests]

    return{
        "handle":handle,
        "contest_attended":len(contests),
        "best_rank":min(rank),
        "worst_rank":max(rank),
        "max_rating":max(rating),
        "current_rating":rating[-1]
    }


async def get_rating_history(handle:str):
    contests=await get_contests(handle)
    return [
        {
            "contest_name":c["contestName"],
            "old_rating":c["oldRating"],
            "new_rating":c["newRating"]
        }
        for c in contests
    ]
