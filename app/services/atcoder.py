import httpx
from bs4 import BeautifulSoup
from datetime import datetime


async def fetch_profile(handle: str):
    history_url = f"https://atcoder.jp/users/{handle}/history/json"

    async with httpx.AsyncClient() as client:
        response = await client.get(history_url)
        response.raise_for_status()
        data = response.json()

    rated_history = [
        item for item in data
        if item.get("IsRated", False)
    ]

    current_rating = (
        rated_history[-1].get("NewRating")
        if rated_history else None
    )

    max_rating = (
        max(
            item.get("NewRating", 0)
            for item in rated_history
        )
        if rated_history else None
    )

    profile_url = f"https://atcoder.jp/users/{handle}"

    async with httpx.AsyncClient() as client:
        response = await client.get(profile_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

    affiliation = None

    for row in soup.select("table.dl-table tr"):
        cells = row.find_all(
            ["th", "td"],
            recursive=False
        )

        if (
            len(cells) >= 2
            and cells[0].get_text(strip=True) == "Affiliation"
        ):
            affiliation = cells[1].get_text(" ", strip=True)
            break

    return {
        "handle": handle,
        "current_rating": current_rating,
        "max_rating": max_rating,
        "contests_participated": len(rated_history),
        "affiliation": affiliation
    }


async def fetch_solved_count(handle: str):
    url = "https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            params={
                "user": handle,
                "from_second": 0
            }
        )
        response.raise_for_status()
        data = response.json()

    solved = {
        submission["problem_id"]
        for submission in data
        if submission.get("result") == "AC"
    }

    return {
        "handle": handle,
        "total_solved": len(solved)
    }


async def fetch_rating_history(handle: str):
    url = f"https://atcoder.jp/users/{handle}/history/json"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    history = []

    for r in data:
        if not r.get("IsRated", False):
            continue

        end_time = r.get("EndTime")

        if not end_time:
            continue

        try:
            contest_time = datetime.fromisoformat(
                end_time.replace("Z", "+00:00")
            )
        except (ValueError, TypeError):
            continue

        old_rating = r.get("OldRating")
        new_rating = r.get("NewRating")

        if old_rating is None or new_rating is None:
            continue

        history.append({
            "contest_name": r.get("ContestScreenName"),
            "contest_id": r.get("ContestScreenName"),
            "old_rating": old_rating,
            "new_rating": new_rating,
            "rating_change": new_rating - old_rating,
            "rank": (
                int(r["Place"])
                if r.get("Place") is not None
                else None
            ),
            "contest_time": contest_time
        })

    return history