
from pydantic import BaseModel
from app.models import PlatformType

class SyncResult(BaseModel):
    platform:PlatformType
    handle:str
    success:bool
    new_contests:int=0

class SyncResponse(BaseModel):
    message:str
    results:list[SyncResult]

class PlatformSyncResult(BaseModel):
    success:bool
    new_contests:int