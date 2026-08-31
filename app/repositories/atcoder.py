from sqlalchemy.orm import Session
from app.models.atcoder import AtCoderProfile,AtCoderContestHistory,AtCoderSolvedProblem

def get_atcoder_profile(db:Session,handle:str):
    return db.query(AtCoderProfile).filter(AtCoderProfile.handle==handle).first()

def insert_atcoder_profile(db:Session,data):
    profile=AtCoderProfile(**data)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def update_atcoder_profile(db:Session,profile,data):
    for key,value in data.items():
        setattr(profile,key,value)
    db.commit()
    db.refresh(profile)
    return profile

def get_atcoder_contests(db:Session,profile_id:int):
    return db.query(AtCoderContestHistory).filter(
        AtCoderContestHistory.atcoder_profile_id==profile_id
    ).order_by(AtCoderContestHistory.contest_time).all()

def insert_atcoder_contests(db:Session,contests):
    if contests:
        db.add_all([AtCoderContestHistory(**x) for x in contests])
        db.commit()

def get_atcoder_solved(db:Session,profile_id:int):
    return db.query(AtCoderSolvedProblem).filter(
        AtCoderSolvedProblem.atcoder_profile_id==profile_id
    ).all()

def insert_atcoder_solved(db:Session,problems):
    if problems:
        db.add_all([AtCoderSolvedProblem(**x) for x in problems])
        db.commit()