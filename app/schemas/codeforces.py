
from pydantic import BaseModel

class ProfileResponse(BaseModel):
    handle:str
    rating:int | None=None
    max_rating:int | None=None
    rank:str | None=None
    first_name:str | None=None
    last_name:str | None=None

class SolvedResponse(BaseModel):
    handle:str
    problems_solved:int

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
    rating_gain:int
    rating_update_time:int
    rank:int
    contest_id:int