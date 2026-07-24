
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.schemas.auth import RegisterRequest
from app.repositories.user import get_user_by_email,get_user_by_username,create_user,get_user_by_identifier
from app.core.security import hash_password,verify_password,create_access_token
from fastapi.security import OAuth2PasswordRequestForm

def register_user(db:Session,user:RegisterRequest):
    existing_user=get_user_by_username(db,user.username)
    if(existing_user):
        raise HTTPException(status_code=400,detail="User already exists")
    existing_eamil=get_user_by_email(db,user.email)
    if(existing_eamil):
        raise HTTPException(status_code=400,detail="email already exists")
    user_details={
        "username":user.username,
        "email":user.email,
        "password_hash":hash_password(user.password)
    }
    return create_user(db,user_details)

def login_user(db:Session,form_data:OAuth2PasswordRequestForm):
    user_details=get_user_by_identifier(db,form_data.username)

    if not user_details or not verify_password(form_data.password,user_details.password_hash):
        raise HTTPException(status_code=401,detail="Invalid Credentials")
    
    token=create_access_token({
        "sub":user_details.username
        })
    
    return {
        "token_type":"bearer",
        "access_token":token
    }