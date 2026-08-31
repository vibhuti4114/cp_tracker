from pydantic import BaseModel
from datetime import datetime

class ProfileResponse(BaseModel):
    handle:str
    current_rating:int|None
    max_rating:int|None
    contests_participated:int
    affiliation:str|None=None

class SolvedResponse(BaseModel):
    handle:str
    total_solved:int

class ContestHistoryItem(BaseModel):
    contest_name:str|None
    contest_id:str|None
    old_rating:int|None
    new_rating:int|None
    rank:int|None
    participated_at:datetime

class ContestResponse(BaseModel):
    history:list[ContestHistoryItem]
