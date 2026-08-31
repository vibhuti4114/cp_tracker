
from app.repositories.linked_account import get_user_linked_accounts,create_linked_account,get_linked_account,update_verification_token,verify_account,unverify_accounts,delete_linked_account
from sqlalchemy.orm import Session
from app.models import User,PlatformType
from fastapi import HTTPException
from app.services.codeforces import fetch_profile as fetch_codeforces_profile
from app.services.leetcode import fetch_profile as fetch_leetcode_profile
from app.services.atcoder import fetch_profile as fetch_atcoder_profile
from app.services.codechef import fetch_profile as fetch_codechef_profile
import string,secrets


def get_all_accounts(db:Session,user:User):
    return get_user_linked_accounts(db,user.id)


async def link_account(db:Session,user:User,handle:str,platform:PlatformType):

    existing=get_linked_account(db,user.id,platform,handle)

    if existing:
        raise HTTPException(status_code=409,detail="Account already linked")

    if platform==PlatformType.codeforces:
        valid=await fetch_codeforces_profile(handle)
    elif platform==PlatformType.leetcode:
        valid=await fetch_leetcode_profile(handle)
    elif platform==PlatformType.atcoder:
        valid=await fetch_atcoder_profile(handle)
    elif platform==PlatformType.codechef:
        valid=await fetch_codechef_profile(handle)
    else:
        raise HTTPException(status_code=400,detail="Unsupported platform")

    if not valid:
        raise HTTPException(status_code=404,detail="Account not found")

    return create_linked_account(db,user.id,platform,handle)

def delete_account(db:Session,user:User,handle:str,platform:PlatformType):
    result=delete_linked_account(db,user.id,platform,handle)
    if result.rowcount==0:
       raise HTTPException(status_code=401,detail="invalid platform or handle")
    return{
        "platform":platform,
        "handle":handle
    }


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

    if not account:
        raise HTTPException(status_code=404,detail="Account Not found")

    if platform==PlatformType.codeforces:
        profile=await fetch_codeforces_profile(handle)
        verification_value=profile.get("first_name")

    elif platform==PlatformType.leetcode:
        profile=await fetch_leetcode_profile(handle)
        verification_value=profile.get("real_name")

    elif platform==PlatformType.atcoder:
        profile=await fetch_atcoder_profile(handle)
        verification_value=profile.get("affiliation")

    elif platform==PlatformType.codechef:
        profile=await fetch_codechef_profile(handle)
        verification_value=profile.get("name")

    else:
        raise HTTPException(status_code=400,detail="Unsupported platform")

    if verification_value!=account.verification_token:
        raise HTTPException(
            status_code=409,
            detail="Verification token not found in profile."
        )

    unverify_accounts(db,handle,platform)
    verify_account(db,account.id)

    return {
        "verified":True
    }