from fastapi import APIRouter
from datetime import datetime
from app.schemas.leetcode import LeetCodeProfileResponse
from app.services.leetcode import fetch_profile
from app.schemas.leetcode import LeetCodeContestResponse
from app.services.leetcode import fetch_contests

router=APIRouter(prefix="/leetcode",tags=["LeetCode"])

@router.get("/{handle}",response_model=LeetCodeProfileResponse)
async def get_leetcode_profile(handle:str):
    return await fetch_profile(handle)

@router.get("/{handle}/contests",response_model=LeetCodeContestResponse)
async def get_leetcode_contests(handle:str):
    data=await fetch_contests(handle)

    ranking=data["ranking"]
    history=data["history"]

    return {
        "attended_contests":ranking["attendedContestsCount"] if ranking else 0,
        "rating":ranking["rating"] if ranking else None,
        "global_ranking":ranking["globalRanking"] if ranking else None,
        "total_participants":ranking["totalParticipants"] if ranking else None,
        "top_percentage":ranking["topPercentage"] if ranking else None,
        "history":[
            {
                "contest_id":contest["contest"]["title"],
                "contest_name":contest["contest"]["title"],
                "rank":contest["ranking"],
                "rating":contest["rating"],
                "rating_change":None,
                "contest_time":datetime.fromtimestamp(
                    contest["contest"]["startTime"]
                )
            }
            for contest in history
            if contest["attended"]
        ]
    }