import httpx
from datetime import datetime

async def fetch_profile(handle:str):
    url=f"https://atcoder.jp/users/{handle}/history/json"

    async with httpx.AsyncClient() as client:
        response=await client.get(url)
        response.raise_for_status()
        data=response.json()

    if not data:
        return{
            "handle":handle,
            "current_rating":None,
            "max_rating":None,
            "contests_participated":0,
            "affiliation":None
        }

    current_rating=data[-1]["NewRating"]
    max_rating=max(item["NewRating"] for item in data)

    profile_url=f"https://atcoder.jp/users/{handle}"

    async with httpx.AsyncClient() as client:
        profile_response=await client.get(profile_url)
        profile_response.raise_for_status()
        html=profile_response.text

    import re

    match=re.search(
        r'<th>Affiliation</th>\s*<td>(.*?)</td>',
        html,
        re.DOTALL
    )

    affiliation=None

    if match:
        affiliation=re.sub("<.*?>","",match.group(1)).strip()

    return{
        "handle":handle,
        "current_rating":current_rating,
        "max_rating":max_rating,
        "contests_participated":len(data),
        "affiliation":affiliation
    }


async def fetch_solved_count(handle:str):
    url="https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions"

    async with httpx.AsyncClient() as client:
        response=await client.get(
            url,
            params={
                "user":handle,
                "from_second":0
            }
        )
        response.raise_for_status()
        data=response.json()

    solved=set()

    for submission in data:
        if submission["result"]=="AC":
            solved.add(submission["problem_id"])

    return{
        "handle":handle,
        "total_solved":len(solved)
    }


async def fetch_rating_history(handle:str):
    url=f"https://atcoder.jp/users/{handle}/history/json"

    async with httpx.AsyncClient() as client:
        response=await client.get(url)
        response.raise_for_status()
        data=response.json()

    history=[]

    for r in data:
        if not r.get("IsRated",False):
            continue

        history.append({
            "contest_name":r.get("ContestScreenName"),
            "contest_id":r.get("ContestScreenName"),
            "old_rating":r.get("OldRating"),
            "new_rating":r.get("NewRating"),
            "rank":str(r.get("Place")) if r.get("Place") is not None else None,
            "participated_at":datetime.fromisoformat(
                r["EndTime"].replace("Z","+00:00")
            )
        })

    return history