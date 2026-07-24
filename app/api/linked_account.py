
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.schemas.linked_account import LinkAccountCreate,LinkedAccountResponse,VerificationCompleteResponse,VerificationStartResponse,VerifyAccountRequest,PlatformType
from app.models import User
from app.services.linked_account import get_all_accounts,link_account,start_verification,complete_verification
from app.core.security import get_current_user

router=APIRouter(
    prefix="/accounts",
    tags=["accounts"]
)

@router.get("",response_model=list[LinkedAccountResponse])
def get_accounts(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    return get_all_accounts(db,user)

@router.post("",response_model=LinkedAccountResponse)
async def add_account(request:LinkAccountCreate,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    return await link_account(db,user,request.handle,request.platform)

@router.post("/verify/start",response_model=VerificationStartResponse)
def start_verify(request:VerifyAccountRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    return start_verification(db,request.handle,request.platform,user)

@router.post("/verify/complete",response_model=VerificationCompleteResponse)
async def complete_verify(request:VerifyAccountRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    return await complete_verification(db,request.handle,request.platform,user)