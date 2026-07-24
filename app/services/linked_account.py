
from app.repositories.linked_account import get_user_linked_accounts,create_linked_account,get_linked_account,update_verification_token,verify_account,unverify_accounts
from sqlalchemy.orm import Session
from app.models import User
from app.models import PlatformType
from fastapi import HTTPException,Depends
from app.services.codeforces import get_profile
import string,secrets


def get_all_accounts(db:Session,user:User):
    return get_user_linked_accounts(db,user.id)


async def link_account(db:Session,user:User,handle:str,platform:PlatformType):
    existing=get_linked_account(db,user.id,platform,handle)
    if(existing):
        raise HTTPException(status_code=409,detail="Account already linked")
    valid=await get_profile(handle,db)
    if(not valid):
        raise HTTPException(status_code=401,detail="Invalid credentials")
    return create_linked_account(db,user.id,platform,handle)


def generate_token():
    alphabet=string.ascii_uppercase+string.digits
    token=''.join(secrets.choice(alphabet) for _ in range(8))
    return token


def start_verification(db:Session,handle:str,platform:PlatformType,user:User):
    account=get_linked_account(db,user.id,platform,handle)
    if account:
        token=generate_token()
        update_verification_token(db,account.id,token)
    else:
        raise HTTPException(status_code=404,detail="Account Not found")
    return {
        "token":token
    }


async def complete_verification(db:Session,handle:str,platform:PlatformType,user:User):
    account=get_linked_account(db,user.id,platform,handle)
    if account:
        profile=await get_profile(handle,db,False)
        if profile["first_name"]==account.verification_token:
            unverify_accounts(db,handle,platform)
            verify_account(db,account.id)
        else:
            raise HTTPException(status_code=409,detail="Verification token not found in your Codeforces first name.")
    else:
        raise HTTPException(status_code=404,detail="Account Not found")
    return {
        "verified":True
    }
        