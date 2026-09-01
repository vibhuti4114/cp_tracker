from app.models import PlatformType
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.user import get_user_by_username
from app.repositories.codeforces import get_codeforces_profile
from app.repositories.leetcode import get_leetcode_profile
from app.repositories.atcoder import get_atcoder_profile, get_atcoder_solved
from app.repositories.codechef import get_codechef_profile

from app.services.codeforces import fetch_solved_count as fetch_codeforces_solved_count, fetch_profile as fetch_codeforces_profile
from datetime import datetime as _dt
from app.services.leetcode import fetch_profile as fetch_leetcode_profile, fetch_contests as fetch_leetcode_contests
from app.services.atcoder import fetch_profile as fetch_atcoder_profile
from app.services.codechef import fetch_profile as fetch_codechef_profile

def dashboard_data(db:Session,username:str,current_user=None):
    user=get_user_by_username(db,username)

    if user is None:
        raise HTTPException(status_code=404,detail="User Not Found")

    # Return the list of linked accounts for the dashboard summary view
    return user.accounts
async def account_data(db:Session,username:str,linked_id:int,current_user=None):
    user=get_user_by_username(db,username)

    if user is None:
        raise HTTPException(status_code=404,detail="User Not Found")

    # compute aggregated platform counts across all linked accounts
    platform_counts: dict[str,int] = {}
    difficulty_counts: dict[str,int] = {"easy":0,"medium":0,"hard":0}

    for acc in user.accounts:
        p = acc.platform
        h = acc.handle
        count = 0

        try:
            if p==PlatformType.leetcode:
                profile = get_leetcode_profile(db,h)
                if profile:
                    count = int(getattr(profile,"total_solved",0) or 0)
                    # add difficulty breakdown from stored leetcode profile
                    difficulty_counts["easy"] += int(getattr(profile,"easy_solved",0) or 0)
                    difficulty_counts["medium"] += int(getattr(profile,"medium_solved",0) or 0)
                    difficulty_counts["hard"] += int(getattr(profile,"hard_solved",0) or 0)

            elif p==PlatformType.codechef:
                profile = get_codechef_profile(db,h)
                if profile:
                    count = int(getattr(profile,"problems_solved",0) or 0)

            elif p==PlatformType.atcoder:
                profile = get_atcoder_profile(db,h)
                if profile:
                    solved = get_atcoder_solved(db,profile.id)
                    count = len(solved) if solved is not None else 0

            elif p==PlatformType.codeforces:
                # codeforces solved count not stored; call service
                try:
                    solved = await fetch_codeforces_solved_count(h)
                    count = int(solved.get("problems_solved",0) or 0)
                except Exception:
                    count = 0

        except Exception:
            count = 0

        key = p.name if hasattr(p, "name") else str(p)
        platform_counts[key] = platform_counts.get(key,0) + count

    # normalize difficulty_counts -- if all zero, set to None so frontend can fallback
    if all(v==0 for v in difficulty_counts.values()):
        difficulty_counts = None

    # now find requested linked account and return its profile enriched with counts
    for account in user.accounts:
        if account.id==linked_id:

            platform = account.platform
            handle = account.handle

            if platform==PlatformType.codeforces:
                profile = get_codeforces_profile(db,handle)
                if not profile:
                    raise HTTPException(status_code=404,detail="Profile not found")

                return {
                    "id": account.id,
                    "handle": profile.handle,
                    "rank": getattr(profile,"rank",None),
                    "rating": getattr(profile,"rating",None),
                    "max_rating": getattr(profile,"max_rating",None),
                    "first_name": getattr(profile,"first_name",None),
                    "last_name": getattr(profile,"last_name",None),
                    "updated_at": getattr(profile,"updated_at",None) or _dt.utcnow(),
                    "contests": getattr(profile,"contests",[]),
                    "difficulty_counts": difficulty_counts,
                    "platform_counts": platform_counts
                }

            if platform==PlatformType.leetcode:
                profile = get_leetcode_profile(db,handle)
                if not profile:
                    # try fetching live profile if not persisted; on failure return minimal response
                    try:
                        live = await fetch_leetcode_profile(handle)
                        return {
                            "id": account.id,
                            "handle": live.get("handle"),
                            "rank": None,
                            "rating": live.get("ranking"),
                            "max_rating": None,
                            "first_name": live.get("real_name"),
                            "last_name": None,
                            "updated_at": _dt.utcnow(),
                            "contests": [],
                            "difficulty_counts": difficulty_counts,
                            "platform_counts": platform_counts
                        }
                    except Exception:
                        from datetime import datetime as _dt
                        return {
                            "id": account.id,
                            "handle": handle,
                            "rank": None,
                            "rating": None,
                            "max_rating": None,
                            "first_name": None,
                            "last_name": None,
                            "updated_at": _dt.utcnow(),
                            "contests": [],
                            "difficulty_counts": difficulty_counts,
                            "platform_counts": platform_counts
                        }

                return {
                    "id": account.id,
                    "handle": profile.handle,
                    "rank": None,
                    "rating": getattr(profile,"ranking",None),
                    "max_rating": None,
                    "first_name": getattr(profile,"real_name",None),
                    "last_name": None,
                    "updated_at": getattr(profile,"updated_at",None) or _dt.utcnow(),
                    "contests": getattr(profile,"contests",[]),
                    "difficulty_counts": difficulty_counts,
                    "platform_counts": platform_counts
                }

            if platform==PlatformType.atcoder:
                profile = get_atcoder_profile(db,handle)
                if not profile:
                    try:
                        live = await fetch_atcoder_profile(handle)
                        return {
                            "id": account.id,
                            "handle": live.get("handle"),
                            "rank": None,
                            "rating": live.get("current_rating"),
                            "max_rating": live.get("max_rating"),
                            "first_name": None,
                            "last_name": None,
                               "updated_at": _dt.utcnow(),
                            "contests": [],
                            "difficulty_counts": difficulty_counts,
                            "platform_counts": platform_counts
                        }
                    except Exception:
                        from datetime import datetime as _dt
                        return {
                            "id": account.id,
                            "handle": handle,
                            "rank": None,
                            "rating": None,
                            "max_rating": None,
                            "first_name": None,
                            "last_name": None,
                            "updated_at": _dt.utcnow(),
                            "contests": [],
                            "difficulty_counts": difficulty_counts,
                            "platform_counts": platform_counts
                        }

                return {
                    "id": account.id,
                    "handle": profile.handle,
                    "rank": None,
                    "rating": getattr(profile,"current_rating",None),
                    "max_rating": getattr(profile,"max_rating",None),
                    "first_name": None,
                    "last_name": None,
                    "updated_at": getattr(profile,"updated_at",None) or _dt.utcnow(),
                    "contests": getattr(profile,"contests",[]),
                    "difficulty_counts": difficulty_counts,
                    "platform_counts": platform_counts
                }

            if platform==PlatformType.codechef:
                profile = get_codechef_profile(db,handle)
                if not profile:
                    try:
                        live = await fetch_codechef_profile(handle)
                        return {
                            "id": account.id,
                            "handle": live.get("handle"),
                            "rank": None,
                            "rating": live.get("current_rating"),
                            "max_rating": live.get("max_rating"),
                            "first_name": live.get("name"),
                            "last_name": None,
                               "updated_at": _dt.utcnow(),
                            "contests": [],
                            "difficulty_counts": difficulty_counts,
                            "platform_counts": platform_counts
                        }
                    except Exception:
                        from datetime import datetime as _dt
                        return {
                            "id": account.id,
                            "handle": handle,
                            "rank": None,
                            "rating": None,
                            "max_rating": None,
                            "first_name": None,
                            "last_name": None,
                            "updated_at": _dt.utcnow(),
                            "contests": [],
                            "difficulty_counts": difficulty_counts,
                            "platform_counts": platform_counts
                        }

                return {
                    "id": account.id,
                    "handle": profile.handle,
                    "rank": None,
                    "rating": getattr(profile,"current_rating",None),
                    "max_rating": getattr(profile,"max_rating",None),
                    "first_name": getattr(profile,"name",None),
                    "last_name": None,
                    "updated_at": getattr(profile,"updated_at",None) or _dt.utcnow(),
                    "contests": [],
                    "difficulty_counts": difficulty_counts,
                    "platform_counts": platform_counts
                }

            raise HTTPException(status_code=400,detail="Unsupported platform")

    raise HTTPException(status_code=403,detail="account is not linked to this user")