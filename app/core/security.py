
from passlib.context import CryptContext
from fastapi import HTTPException,Depends
from sqlalchemy.orm import Session
from jose import jwt,JWTError
from app.core.config import *
from datetime import datetime,timedelta,timezone
from fastapi.security import OAuth2PasswordBearer
from app.repositories.user import get_user_by_username
from app.database.dependencies import get_db

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")

credential_exception=HTTPException(status_code=401,detail="could not validate credentials")

pwd_context= CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_password(password:str)->str:
    return pwd_context.hash(password)

def verify_password(password:str,hashed_password:str)->bool:
    return pwd_context.verify(password,hashed_password)

def create_access_token(data:dict)->str:
    payload=data.copy()
    expire_time=datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_TIME)
    payload["exp"]=expire_time
    return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)

def verify_access_token(token:str):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        return payload
    except JWTError :
        raise credential_exception

def get_current_user(db:Session=Depends(get_db),token:str=Depends(oauth2_scheme)):
    payload=verify_access_token(token)
    username=payload["sub"]
    user=get_user_by_username(db,username)
    if not user :
        raise credential_exception
    return user
