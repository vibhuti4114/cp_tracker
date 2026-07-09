
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.cf_profile import CachedProfile

def get_cached_profile(db:Session,handle:str):
    return(
        db.query(CachedProfile).filter(func.lower(CachedProfile.handle)==handle.lower()).first()
    )

def create_catched_profile(db:Session,profile_details:dict):
    new=CachedProfile(
        handle=profile_details["handle"],
        rank=profile_details["rank"],
        max_rating=profile_details["max_rating"],
        rating=profile_details["rating"]
    )
    db.add(new)
    db.commit()
    db.refresh(new)
    return new