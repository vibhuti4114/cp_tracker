from app.models import User, PlatformType, LinkedAccount
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.codeforces import (
    fetch_profile as fetch_codeforces_profile,
    fetch_rating_history as fetch_codeforces_history
)
from app.repositories.codeforces import (
    get_codeforces_profile,
    update_codeforces_profile,
    insert_codeforces_profile,
    get_max_rating_update_time,
    insert_contest
)
from app.services.leetcode import (
    fetch_profile as fetch_leetcode_profile,
    fetch_contests
)
from app.repositories.leetcode import (
    get_leetcode_profile,
    insert_leetcode_profile,
    update_leetcode_profile,
    get_latest_leetcode_contest,
    insert_leetcode_contests
)
from app.services.atcoder import (
    fetch_profile as fetch_atcoder_profile,
    fetch_rating_history as fetch_atcoder_history
)
from app.repositories.atcoder import (
    get_atcoder_profile,
    insert_atcoder_profile,
    update_atcoder_profile,
    get_atcoder_contests,
    insert_atcoder_contests
)
from app.services.codechef import (
    fetch_profile as fetch_codechef_profile,
    fetch_rating_history as fetch_codechef_history
)
from app.repositories.codechef import (
    get_codechef_profile,
    insert_codechef_profile,
    update_codechef_profile,
    get_codechef_contests,
    insert_codechef_contests
)
import asyncio
from app.schemas.sync import PlatformSyncResult, SyncResult


async def sync_codeforces(
    db: Session,
    account: LinkedAccount
) -> PlatformSyncResult:

    profile, contests = await asyncio.gather(
        fetch_codeforces_profile(account.handle),
        fetch_codeforces_history(account.handle)
    )

    db_profile = get_codeforces_profile(db, account.handle)

    if db_profile:
        db_profile = update_codeforces_profile(
            db,
            db_profile,
            profile
        )
    else:
        db_profile = insert_codeforces_profile(
            db,
            profile
        )

    max_time = get_max_rating_update_time(
        db,
        db_profile.id
    )

    new_contests = []

    for contest in contests:
        if (
            max_time is None
            or contest["rating_update_time"] > max_time
        ):
            contest["codeforces_profile_id"] = db_profile.id
            new_contests.append(contest)

    if new_contests:
        insert_contest(db, new_contests)

    return {
        "success": True,
        "new_contests": len(new_contests)
    }


async def sync_leetcode(
    db: Session,
    account: LinkedAccount
) -> PlatformSyncResult:

    profile_data, contest_data = await asyncio.gather(
        fetch_leetcode_profile(account.handle),
        fetch_contests(account.handle)
    )

    profile = get_leetcode_profile(
        db,
        account.handle
    )

    if profile:
        profile = update_leetcode_profile(
            db,
            profile,
            profile_data
        )
    else:
        profile = insert_leetcode_profile(
            db,
            profile_data
        )

    latest = get_latest_leetcode_contest(
        db,
        profile.id
    )

    latest_time = latest.contest_time if latest else None
    previous_rating = latest.rating if latest else None

    new_contests = []

    for contest in contest_data["history"]:

        if not contest.get("attended"):
            continue

        contest_info = contest.get("contest") or {}

        start_time = contest_info.get("startTime")

        if start_time is None:
            continue

        contest_time = datetime.fromtimestamp(
            start_time
        )

        if (
            latest_time is not None
            and contest_time <= latest_time
        ):
            continue

        rating = contest.get("rating")
        rating_change = None

        if (
            previous_rating is not None
            and rating is not None
        ):
            rating_change = rating - previous_rating

        new_contests.append({
            "leetcode_profile_id": profile.id,
            "contest_id": contest_info.get("title"),
            "contest_name": contest_info.get("title"),
            "rank": contest.get("ranking"),
            "rating": rating,
            "rating_change": rating_change,
            "contest_time": contest_time
        })

        if rating is not None:
            previous_rating = rating

    if new_contests:
        insert_leetcode_contests(
            db,
            new_contests
        )

    return {
        "success": True,
        "new_contests": len(new_contests)
    }


async def sync_atcoder(
    db: Session,
    account: LinkedAccount
) -> PlatformSyncResult:

    profile_data, contest_data = await asyncio.gather(
        fetch_atcoder_profile(account.handle),
        fetch_atcoder_history(account.handle)
    )

    profile = get_atcoder_profile(
        db,
        account.handle
    )

    if profile:
        profile = update_atcoder_profile(
            db,
            profile,
            profile_data
        )
    else:
        profile = insert_atcoder_profile(
            db,
            profile_data
        )

    existing_contests = get_atcoder_contests(
        db,
        profile.id
    )

    existing_contest_ids = {
        contest.contest_id
        for contest in existing_contests
    }

    new_contests = []

    for contest in contest_data:

        contest_id = contest.get("contest_id")
        contest_time = contest.get("contest_time")

        if not contest_id or not contest_time:
            continue

        if contest_id in existing_contest_ids:
            continue

        if contest_time.tzinfo is not None:
            contest_time = contest_time.replace(tzinfo=None)

        new_contests.append({
            "atcoder_profile_id": profile.id,
            "contest_id": contest_id,
            "contest_name": contest["contest_name"],
            "rank": contest["rank"],
            "old_rating": contest["old_rating"],
            "new_rating": contest["new_rating"],
            "rating_change": contest["rating_change"],
            "contest_time": contest_time
        })

        existing_contest_ids.add(contest_id)

    if new_contests:
        insert_atcoder_contests(
            db,
            new_contests
        )

    return {
        "success": True,
        "new_contests": len(new_contests)
    }


async def sync_codechef(
    db: Session,
    account: LinkedAccount
) -> PlatformSyncResult:

    profile_data, contest_data = await asyncio.gather(
        fetch_codechef_profile(account.handle),
        fetch_codechef_history(account.handle)
    )

    profile = get_codechef_profile(
        db,
        account.handle
    )

    if profile:
        profile = update_codechef_profile(
            db,
            profile,
            profile_data
        )
    else:
        profile = insert_codechef_profile(
            db,
            profile_data
        )

    existing_contests = get_codechef_contests(
        db,
        profile.id
    )

    latest_time = (
        existing_contests[-1].participated_at
        if existing_contests
        else None
    )

    new_contests = []

    for contest in contest_data:

        contest_time = contest["participated_at"]

        if (
            latest_time is not None
            and contest_time <= latest_time
        ):
            continue

        new_contests.append({
            "codechef_profile_id": profile.id,
            "contest_name": contest["contest_name"],
            "contest_id": contest["contest_id"],
            "old_rating": contest["old_rating"],
            "new_rating": contest["new_rating"],
            "rank": contest["rank"],
            "participated_at": contest_time
        })

    if new_contests:
        insert_codechef_contests(
            db,
            new_contests
        )

    return {
        "success": True,
        "new_contests": len(new_contests)
    }


async def sync(
    user: User,
    db: Session
):

    results = []

    for account in user.accounts:

        if account.platform == PlatformType.codeforces:

            result = await sync_codeforces(
                db,
                account
            )

        elif account.platform == PlatformType.leetcode:

            result = await sync_leetcode(
                db,
                account
            )

        elif account.platform == PlatformType.atcoder:

            result = await sync_atcoder(
                db,
                account
            )

        elif account.platform == PlatformType.codechef:

            result = await sync_codechef(
                db,
                account
            )

        else:
            continue

        results.append(
            SyncResult(
                platform=account.platform,
                handle=account.handle,
                success=result["success"],
                new_contests=result["new_contests"]
            )
        )

    return {
        "message": "Sync complete",
        "results": results
    }