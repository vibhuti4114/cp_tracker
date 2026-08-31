
from fastapi import APIRouter,Depends
from app.services.dashboard import dashboard_data,account_data
from app.schemas.dashboard import DashboardSummary,DashboardAccountResponse
from app.database.dependencies import get_db
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.models import User


router=APIRouter(
    prefix="/dashboard",
    tags=["dashboard"]
)

@router.get("/u/{username}",response_model=list[DashboardSummary])
def get_dashboard(user:User=Depends(get_current_user)):
    return dashboard_data(user)


@router.get("/u/{username}/{linked_account_id}",response_model=DashboardAccountResponse)
def get_dashboard(id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    return account_data(user,db,id)
