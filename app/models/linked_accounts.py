
from enum import Enum as pythonEnum
from sqlalchemy import Column,Integer,String,DateTime,ForeignKey,Enum,Boolean,UniqueConstraint
from app.database.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class PlatformType(pythonEnum):
    codeforces="CODEFORCES"
    leetcode="LEETCODE"
    atcoder="ATCODER"
    codechef="CODECHEF"

class LinkedAccount(Base):
    __tablename__="linked_accounts"
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False,index=True)
    platform=Column(Enum(PlatformType),nullable=False)
    handle=Column(String,nullable=False)
    created_at=Column(DateTime,default=datetime.utcnow)
    verified=Column(Boolean,default=False)
    verification_token=Column(String,nullable=True)
    user=relationship("User",back_populates="accounts")