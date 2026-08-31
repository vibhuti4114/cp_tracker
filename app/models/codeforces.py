
from sqlalchemy import Column,Integer,String,DateTime,ForeignKey,UniqueConstraint
from app.database.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class CodeforcesProfile(Base):
    __tablename__="codeforces_profile"
    id=Column(Integer,primary_key=True, index=True)
    handle=Column(String,unique=True,nullable=False,index=True)
    rank=Column(String)
    rating=Column(Integer)
    max_rating=Column(Integer)
    first_name=Column(String)
    last_name=Column(String)
    updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    contests=relationship("CodeforcesContestHistory",back_populates="codeforces_profile")

class CodeforcesContestHistory(Base):
    __tablename__="codeforces_contest_history"
    id=Column(Integer,primary_key=True,index=True)
    codeforces_profile_id=Column(Integer,ForeignKey("codeforces_profile.id"),nullable=False,index=True)
    contest_id=Column(Integer,nullable=False)
    contest_name=Column(String,nullable=False)
    rank=Column(Integer)
    old_rating=Column(Integer,nullable=False)
    new_rating=Column(Integer,nullable=False)
    rating_gain=Column(Integer,nullable=False)
    rating_update_time=Column(Integer,nullable=False)
    __table_args__=(
        UniqueConstraint("codeforces_profile_id","contest_id"),
    )
    codeforces_profile=relationship("CodeforcesProfile",back_populates="contests")