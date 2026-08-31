
from sqlalchemy.orm import Session
from app.models import LinkedAccount
from app.models import PlatformType
from sqlalchemy import func,update,delete

def create_linked_account(db:Session,user_id:int,platform:PlatformType,handle:str):
    linked=LinkedAccount(user_id=user_id,handle=handle,platform=platform)
    db.add(linked)
    db.commit()
    db.refresh(linked)
    return linked

def get_user_linked_accounts(db:Session,user_id:int):
    return db.query(LinkedAccount).filter(LinkedAccount.user_id==user_id).all()

def get_linked_account(db:Session,user_id:int,platform:PlatformType,handle:str):
    return db.query(LinkedAccount).where(LinkedAccount.user_id==user_id, LinkedAccount.platform==platform, func.lower(LinkedAccount.handle)==handle.lower()).first()

def delete_linked_account(db:Session,user_id:int,platform:PlatformType,handle:str):
    statement=delete(LinkedAccount).where(LinkedAccount.user_id==user_id, LinkedAccount.platform==platform,LinkedAccount.handle==handle)
    result=db.execute(statement)
    db.commit()
    return result

def update_verification_token(db:Session,id:int,token:str):
    upd=update(LinkedAccount).where(LinkedAccount.id==id).values(verification_token=token)
    db.execute(upd)
    db.commit()

def unverify_accounts(db:Session,handle:str,platform:PlatformType):
    upd=update(LinkedAccount).where(LinkedAccount.handle==handle,LinkedAccount.platform==platform).values(verified=False)
    db.execute(upd)
    db.commit()

def verify_account(db:Session,id:int):
    upd=update(LinkedAccount).where(LinkedAccount.id==id).values(verified=True,verification_token=None)
    db.execute(upd)
    db.commit()