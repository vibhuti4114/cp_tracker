
from pydantic import BaseModel

class ProfileResponse(BaseModel):
    handle:str
    rating:int | None=None
    max_rating:int | None=None
    rank:str | None=None

class SolvedResponse(BaseModel):
    handle:str
    problems_solved:int

class StatsResponse(BaseModel):
    handle:str
    problems_solved:int
    average_rating_solved:int | None=None
    max_rating_solved:int| None=None

class TagsResponse(BaseModel):
    handle:str
    tags:dict[str,int]

class ContestResponse(BaseModel):
    handle:str
    contest_attended:int
    best_rank:int | None=None
    worst_rank:int | None=None
    max_rating:int | None=None
    current_rating:int | None=None

class RatingHistoryItem(BaseModel):
    contest_name: str
    old_rating: int
    new_rating: int
    