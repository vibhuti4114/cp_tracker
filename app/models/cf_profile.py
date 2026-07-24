
from sqlalchemy import Column,Integer,String,DateTime
from app.database.database import Base
from datetime import datetime

class CachedProfile(Base):
    __tablename__="cached_profile"
    id=Column(Integer,primary_key=True, index=True)
    handle=Column(String,unique=True,nullable=False)
    rank=Column(String)
    rating=Column(Integer)
    max_rating=Column(Integer)
    first_name=Column(String)
    last_name=Column(String)
    updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)

