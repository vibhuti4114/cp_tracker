
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.schemas.auth import RegisterRequest,UserResponse,Token
from app.services.auth import register_user,login_user
from app.core.security import get_current_user
from app.models import User
from fastapi.security import OAuth2PasswordRequestForm
 
router=APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register",response_model=UserResponse,status_code=201)
def register(user:RegisterRequest,db:Session=Depends(get_db)):
    return register_user(db,user)

@router.post("/login",response_model=Token)
def login(form_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    return login_user(db,form_data)

@router.get("/me",response_model=UserResponse)
def me(current_user:User=Depends(get_current_user)):
    return current_user