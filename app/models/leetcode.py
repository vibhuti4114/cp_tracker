from datetime import datetime
from app.database.database import Base
from sqlalchemy import Column,Integer,String,Float,DateTime,ForeignKey,UniqueConstraint
from sqlalchemy.orm import relationship

class LeetCodeProfile(Base):
    __tablename__="leetcode_profiles"
    id=Column(Integer,primary_key=True,index=True)
    handle=Column(String,unique=True,index=True,nullable=False)
    real_name=Column(String,nullable=True)
    ranking=Column(Integer,nullable=True)
    total_solved=Column(Integer,default=0)
    easy_solved=Column(Integer,default=0)
    medium_solved=Column(Integer,default=0)
    hard_solved=Column(Integer,default=0)
    total_questions=Column(Integer,default=0)
    easy_questions=Column(Integer,default=0)
    medium_questions=Column(Integer,default=0)
    hard_questions=Column(Integer,default=0)
    updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    
    contests=relationship("LeetCodeContestHistory",back_populates="profile",cascade="all, delete-orphan")

class LeetCodeContestHistory(Base):
    __tablename__="leetcode_contest_history"

    id=Column(Integer,primary_key=True,index=True)
    leetcode_profile_id=Column(Integer,ForeignKey("leetcode_profiles.id"),nullable=False)
    contest_id=Column(String,nullable=False)
    contest_name=Column(String,nullable=False)
    rank=Column(Integer)
    rating=Column(Float)
    rating_change=Column(Float)
    contest_time=Column(DateTime,nullable=False)

    profile=relationship("LeetCodeProfile",back_populates="contests")

    __table_args__=(
        UniqueConstraint("leetcode_profile_id","contest_id"),
    )