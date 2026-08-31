from pydantic import BaseModel
from datetime import datetime

class LeetCodeTag(BaseModel):
    tagName:str
    problemsSolved:int

class LeetCodeTags(BaseModel):
    advanced:list[LeetCodeTag]=[]
    intermediate:list[LeetCodeTag]=[]
    fundamental:list[LeetCodeTag]=[]

class LeetCodeProfileResponse(BaseModel):
    handle:str
    real_name:str|None=None
    ranking:int|None=None
    total_solved:int
    easy_solved:int
    medium_solved:int
    hard_solved:int
    total_questions:int
    easy_questions:int
    medium_questions:int
    hard_questions:int
    tags:LeetCodeTags

class LeetCodeContest(BaseModel):
    contest_id: str
    contest_name: str
    rank: int
    rating: float
    rating_change: float | None
    contest_time: datetime

class LeetCodeContestResponse(BaseModel):
    attended_contests:int
    rating:float|None=None
    global_ranking:int|None=None
    total_participants:int|None=None
    top_percentage:float|None=None
    history:list[LeetCodeContest]
