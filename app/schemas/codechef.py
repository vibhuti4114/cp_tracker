from pydantic import BaseModel
from datetime import datetime

class ProfileResponse(BaseModel):
    handle:str
    name:str|None=None
    current_rating:int|None
    max_rating:int|None
    contests_participated:int

class RatingHistoryItem(BaseModel):
    contest_name:str|None
    contest_id:str|None
    old_rating:int
    new_rating:int
    rank:str|None
    participated_at:datetime