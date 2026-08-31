from app.models import PlatformType
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.user import get_user_by_username
from app.repositories.codeforces import get_codeforces_profile
from app.repositories.leetcode import get_leetcode_profile
from app.repositories.atcoder import get_atcoder_profile
from app.repositories.codechef import get_codechef_profile

def dashboard_data(db:Session,username:str,current_user=None):
    user=get_user_by_username(db,username)

    if user is None:
        raise HTTPException(status_code=404,detail="User Not Found")

    can_edit=(current_user is not None and current_user.username==username)

    return{
        "user":user,
        "accounts":user.accounts,
        "can_edit":can_edit
    }

def account_data(db:Session,username:str,linked_id:int):
    user=get_user_by_username(db,username)

    if user is None:
        raise HTTPException(status_code=404,detail="User Not Found")

    for account in user.accounts:
        if account.id==linked_id:

            if account.platform==PlatformType.codeforces:
                return get_codeforces_profile(db,account.handle)

            if account.platform==PlatformType.leetcode:
                return get_leetcode_profile(db,account.handle)

            if account.platform==PlatformType.atcoder:
                return get_atcoder_profile(db,account.handle)

            if account.platform==PlatformType.codechef:
                return get_codechef_profile(db,account.handle)

            raise HTTPException(status_code=400,detail="Unsupported platform")

    raise HTTPException(status_code=403,detail="account is not linked to this user")