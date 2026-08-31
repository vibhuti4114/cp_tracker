
import httpx
from fastapi import HTTPException

BASE_URL = "https://codeforces.com/api"

# ----------------------------------------------------------------------------------------------------
# Helper Function
# ----------------------------------------------------------------------------------------------------

async def fetch_submissions(handle: str):
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

async def fetch_unique_solved(handle:str):
    submission=await fetch_submissions(handle)
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

async def fetch_contests(handle:str):
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

async def fetch_profile(handle :str):
    
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
        "first_name":user.get("firstName"),
        "last_name":user.get("lastName")
    }
    return profile_details

async def fetch_solved_count(handle :str):
    solved=await fetch_unique_solved(handle)

    return {
        "handle": handle,
        "problems_solved": len(solved)
    }

async def fetch_tags(handle:str):
    solved=await fetch_unique_solved(handle)
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


async def build_contest_stats(handle:str):
    contests=await fetch_contests(handle)

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


async def fetch_rating_history(handle:str):
    contests=await fetch_contests(handle)
    return [
        {
            "contest_name":c["contestName"],
            "old_rating":c["oldRating"],
            "new_rating":c["newRating"],
            "rating_gain":c["newRating"]-c["oldRating"],
            "rating_update_time":c["ratingUpdateTimeSeconds"],
            "rank":c["rank"],
            "contest_id":c["contestId"]
        }
        for c in contests
    ]