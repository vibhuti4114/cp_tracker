
from sqlalchemy import func,insert
from sqlalchemy.orm import Session
from app.models import CodeforcesProfile,CodeforcesContestHistory

def get_codeforces_profile(db:Session,handle:str):
    return db.query(CodeforcesProfile).filter(func.lower(CodeforcesProfile.handle)==handle.lower()).first()

def insert_codeforces_profile(db:Session,profile_details:dict):
    profile=CodeforcesProfile(
        handle=profile_details["handle"],
        rank=profile_details["rank"],
        max_rating=profile_details["max_rating"],
        rating=profile_details["rating"],
        first_name=profile_details["first_name"],
        last_name=profile_details["last_name"]
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def update_codeforces_profile(db:Session,profile:CodeforcesProfile,profile_details:dict):
    profile.rank=profile_details["rank"]
    profile.rating=profile_details["rating"]
    profile.first_name=profile_details["first_name"]
    profile.last_name=profile_details["last_name"]
    profile.max_rating=profile_details["max_rating"]
    db.commit()
    db.refresh(profile)
    return profile

def get_max_rating_update_time(db:Session,id:int):
    return db.query(func.max(CodeforcesContestHistory.rating_update_time)).filter(CodeforcesContestHistory.codeforces_profile_id==id).scalar()

def insert_contest(db:Session,contests:list[dict]):
    db.execute(insert(CodeforcesContestHistory),contests)
    db.commit()