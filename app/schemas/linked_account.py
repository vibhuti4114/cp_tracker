
from pydantic import BaseModel
from datetime import datetime
from app.models import PlatformType

class LinkAccountCreate(BaseModel):
    platform:PlatformType
    handle:str

class LinkedAccountResponse(BaseModel):
    id:int
    platform:PlatformType
    handle:str
    verified:bool
    created_at:datetime
    model_config={
        "from_attributes":True
    }

class VerifyAccountRequest(BaseModel):
    platform:PlatformType
    handle:str

class VerificationStartResponse(BaseModel):
    token:str

class VerificationCompleteResponse(BaseModel):
    verified:bool