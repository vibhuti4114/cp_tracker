import httpx
from fastapi import HTTPException

LEETCODE_GRAPHQL_URL="https://leetcode.com/graphql"

PROFILE_QUERY="""
query getUserProfile($username:String!){
    allQuestionsCount{
        difficulty
        count
    }
    matchedUser(username:$username){
        username
        profile{
            realName
            ranking
        }
        skillStats:tagProblemCounts{
            advanced{
                tagName
                problemsSolved
            }
            intermediate{
                tagName
                problemsSolved
            }
            fundamental{
                tagName
                problemsSolved
            }
        }
        submitStats:submitStatsGlobal{
            acSubmissionNum{
                difficulty
                count
            }
        }
    }
}
"""

CONTEST_QUERY="""
query userContestRankingInfo($username:String!) {
    userContestRanking(username:$username) {
        attendedContestsCount
        rating
        globalRanking
        totalParticipants
        topPercentage
    }
    userContestRankingHistory(username:$username) {
        attended
        rating
        ranking
        contest {
            title
            startTime
        }
    }
}
"""

async def fetch_profile(handle:str):
    payload={
        "query":PROFILE_QUERY,
        "variables":{"username":handle}
    }
    headers={
        "Content-Type":"application/json",
        "Referer":f"https://leetcode.com/u/{handle}/",
        "User-Agent":"Mozilla/5.0"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response=await client.post(LEETCODE_GRAPHQL_URL,json=payload,headers=headers)

    if response.status_code!=200:
        raise HTTPException(status_code=502,detail="Unable to fetch data from LeetCode")

    data=response.json()

    if data.get("errors"):
        raise HTTPException(status_code=404,detail="LeetCode user not found")

    result=data.get("data")

    if not result or not result.get("matchedUser"):
        raise HTTPException(status_code=404,detail="LeetCode user not found")

    user=result["matchedUser"]
    profile=user.get("profile") or {}
    skills=user.get("skillStats") or {}

    solved_stats={
        item["difficulty"]:item["count"]
        for item in user["submitStats"]["acSubmissionNum"]
    }

    question_stats={
        item["difficulty"]:item["count"]
        for item in result["allQuestionsCount"]
    }

    return {
        "handle":user["username"],
        "real_name":profile.get("realName"),
        "ranking":profile.get("ranking"),
        "total_solved":solved_stats.get("All",0),
        "easy_solved":solved_stats.get("Easy",0),
        "medium_solved":solved_stats.get("Medium",0),
        "hard_solved":solved_stats.get("Hard",0),
        "total_questions":question_stats.get("All",0),
        "easy_questions":question_stats.get("Easy",0),
        "medium_questions":question_stats.get("Medium",0),
        "hard_questions":question_stats.get("Hard",0),
        "tags":skills
    }


async def fetch_contests(handle:str):
    payload={
        "query":CONTEST_QUERY,
        "variables":{"username":handle}
    }
    headers={
        "Content-Type":"application/json",
        "Referer":f"https://leetcode.com/u/{handle}/",
        "User-Agent":"Mozilla/5.0"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response=await client.post(LEETCODE_GRAPHQL_URL,json=payload,headers=headers)

    if response.status_code!=200:
        raise HTTPException(status_code=502,detail="Unable to fetch contest data from LeetCode")

    data=response.json()

    if data.get("errors"):
        raise HTTPException(status_code=502,detail="Unable to fetch contest data from LeetCode")

    result=data.get("data") or {}

    ranking=result.get("userContestRanking")
    history=result.get("userContestRankingHistory")

    return {
        "ranking":ranking,
        "history":history or []
    }