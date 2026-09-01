
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
def get_dashboard(username: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return dashboard_data(db, username, user)


@router.get("/u/{username}/{linked_account_id}",response_model=DashboardAccountResponse)
async def get_dashboard_account(username: str, linked_account_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return await account_data(db, username, linked_account_id, user)
