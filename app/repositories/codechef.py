from sqlalchemy.orm import Session
from app.models.codechef import CodeChefProfile,CodeChefContestHistory

def get_codechef_profile(db:Session,handle:str):
    return db.query(CodeChefProfile).filter(CodeChefProfile.handle==handle).first()

def insert_codechef_profile(db:Session,data):
    profile=CodeChefProfile(**data)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def update_codechef_profile(db:Session,profile,data):
    for key,value in data.items():
        setattr(profile,key,value)
    db.commit()
    db.refresh(profile)
    return profile

def get_codechef_contests(db:Session,profile_id:int):
    return db.query(CodeChefContestHistory).filter(
        CodeChefContestHistory.codechef_profile_id==profile_id
    ).order_by(CodeChefContestHistory.participated_at).all()

def insert_codechef_contests(db:Session,contests):
    if contests:
        db.add_all([CodeChefContestHistory(**x) for x in contests])
        db.commit()