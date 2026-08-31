from sqlalchemy import Column,Integer,String,Float,DateTime,ForeignKey,UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.database import Base

class AtCoderProfile(Base):
    __tablename__="atcoder_profiles"
    id=Column(Integer,primary_key=True,index=True)
    handle=Column(String,unique=True,index=True)
    rating=Column(Integer)
    max_rating=Column(Integer)
    updated_at=Column(DateTime)

    contests=relationship("AtCoderContestHistory",back_populates="profile",cascade="all,delete-orphan")
    solved_problems=relationship("AtCoderSolvedProblem",back_populates="profile",cascade="all,delete-orphan")

class AtCoderContestHistory(Base):
    __tablename__="atcoder_contest_history"
    id=Column(Integer,primary_key=True,index=True)
    atcoder_profile_id=Column(Integer,ForeignKey("atcoder_profiles.id"))
    contest_id=Column(String)
    contest_name=Column(String)
    rank=Column(Integer)
    old_rating=Column(Integer)
    new_rating=Column(Integer)
    rating_change=Column(Integer)
    contest_time=Column(DateTime)

    profile=relationship("AtCoderProfile",back_populates="contests")

    __table_args__=(
        UniqueConstraint("atcoder_profile_id","contest_id"),
    )

class AtCoderSolvedProblem(Base):
    __tablename__="atcoder_solved_problems"
    id=Column(Integer,primary_key=True,index=True)
    atcoder_profile_id=Column(Integer,ForeignKey("atcoder_profiles.id"))
    problem_id=Column(String)
    problem_name=Column(String)
    contest_id=Column(String)
    contest_name=Column(String)
    difficulty=Column(Integer)

    profile=relationship("AtCoderProfile",back_populates="solved_problems")

    __table_args__=(
        UniqueConstraint("atcoder_profile_id","problem_id"),
    )