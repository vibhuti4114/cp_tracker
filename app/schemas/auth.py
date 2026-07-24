
from pydantic import BaseModel
from datetime import datetime

class RegisterRequest(BaseModel):
    username :str
    email:str
    password:str

class UserResponse(BaseModel):
    id:int
    username:str
    email:str
    created_at:datetime
    model_config={
        "from_attributes":True
    }

class Token(BaseModel):
    access_token:str
    token_type:str
