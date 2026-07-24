
from sqlalchemy.orm import Session
from app.models import User

def get_user_by_username(db:Session,username:str):
    return(
        db.query(User).filter(User.username==username).first()
    )

def get_user_by_email(db:Session,email:str):
    return(
        db.query(User).filter(User.email==email).first()
    )
    
def create_user(db:Session,user_details:dict):
    user=User(**user_details)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_identifier(db:Session,identifier:str):
    if "@" in identifier:
        return get_user_by_email(db,identifier)
    else:
        return get_user_by_username(db,identifier)
    