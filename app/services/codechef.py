import httpx
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime, timezone

async def fetch_profile(handle:str):
    url=f"https://www.codechef.com/users/{handle}"

    async with httpx.AsyncClient(
        follow_redirects=True,
        headers={
            "User-Agent":"Mozilla/5.0"
        }
    ) as client:
        response=await client.get(url)
        response.raise_for_status()

    html=response.text

    current_rating=None
    max_rating=None
    name=None
    rating_data=[]

    match=re.search(r'"currentRating"\s*:\s*"?(\d+)"?',html)
    if match:
        current_rating=int(match.group(1))

    match=re.search(r'Highest Rating\s*(\d+)',html,re.IGNORECASE)
    if match:
        max_rating=int(match.group(1))

    if max_rating is None:
        match=re.search(r'"highestRating"\s*:\s*"?(\d+)"?',html)
        if match:
            max_rating=int(match.group(1))

    soup=BeautifulSoup(html,"html.parser")

    name_tag=soup.find("h1")

    if name_tag:
        name=name_tag.get_text(" ",strip=True)

    if name==handle:
        name=None

    match=re.search(
        r'(?:all_rating|ratingData)\s*[:=]\s*(\[.*?\])',
        html,
        re.DOTALL
    )

    if match:
        try:
            rating_data=json.loads(match.group(1))
        except json.JSONDecodeError:
            rating_data=[]

    if current_rating is None and rating_data:
        ratings=[
            int(x["rating"])
            for x in rating_data
            if x.get("rating")
        ]

        if ratings:
            current_rating=ratings[-1]

    if max_rating is None and rating_data:
        ratings=[
            int(x["rating"])
            for x in rating_data
            if x.get("rating")
        ]

        if ratings:
            max_rating=max(ratings)

    return{
        "handle":handle,
        "name":name,
        "current_rating":current_rating,
        "max_rating":max_rating,
        "contests_participated":len(rating_data)
    }


async def fetch_rating_history(handle:str):
    url=f"https://www.codechef.com/users/{handle}"

    async with httpx.AsyncClient(
        follow_redirects=True,
        headers={
            "User-Agent":"Mozilla/5.0"
        }
    ) as client:
        response=await client.get(url)

    if response.status_code!=200:
        return []

    html=response.text

    match=re.search(
        r'(?:all_rating|ratingData)\s*[:=]\s*(\[.*?\])',
        html,
        re.DOTALL
    )

    if not match:
        return []

    try:
        rating_data=json.loads(match.group(1))
    except json.JSONDecodeError:
        return []

    history=[]

    for i,r in enumerate(rating_data):
        end_date=r.get("end_date") or r.get("endDate")

        try:
            if end_date:
                fmt="%Y-%m-%d %H:%M:%S" if " " in end_date else "%Y-%m-%d"
                participated_at=datetime.strptime(
                    end_date,fmt
                ).replace(tzinfo=timezone.utc)
            else:
                participated_at=datetime.now(timezone.utc)
        except ValueError:
            participated_at=datetime.now(timezone.utc)

        old_rating=(
            int(rating_data[i-1].get("rating",1500))
            if i>0 else 1500
        )

        new_rating=int(r.get("rating",1500))

        history.append({
            "contest_name":r.get("name") or r.get("contest_name") or r.get("title"),
            "contest_id":r.get("code") or r.get("contest_code") or r.get("contest_id"),
            "old_rating":old_rating,
            "new_rating":new_rating,
            "rank":str(r.get("rank")) if r.get("rank") is not None else None,
            "participated_at":participated_at
        })

    return history