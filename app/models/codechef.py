from sqlalchemy import Column,Integer,String,DateTime,ForeignKey
from app.database.database import Base

class CodeChefProfile(Base):
    __tablename__="codechef_profiles"
    id=Column(Integer,primary_key=True,index=True)
    handle=Column(String,unique=True,index=True,nullable=False)
    current_rating=Column(Integer,nullable=True)
    max_rating=Column(Integer,nullable=True)
    problems_solved=Column(Integer,default=0)
    contests_participated=Column(Integer,default=0)
    updated_at=Column(DateTime,nullable=True)

class CodeChefContestHistory(Base):
    __tablename__="codechef_contest_history"
    id=Column(Integer,primary_key=True,index=True)
    codechef_profile_id=Column(Integer,ForeignKey("codechef_profiles.id"),nullable=False)
    contest_id=Column(String,nullable=True)
    contest_name=Column(String,nullable=True)
    old_rating=Column(Integer,nullable=True)
    new_rating=Column(Integer,nullable=True)
    rank=Column(String,nullable=True)
    participated_at=Column(DateTime,nullable=True)