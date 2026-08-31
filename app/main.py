
from fastapi import FastAPI
from app.api.codeforces import router as cf_router
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.database.database import Base,engine
from app.api.linked_account import router as linked_user_router
from app.api.dashboard import router as dashboard_router
from app.api.leetcode import router as leetcode_router
from app.api.atcoder import router as atcoder_router
from app.api.codechef import router as codechef_router

Base.metadata.create_all(bind=engine)

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    cf_router,
    prefix="/codeforces",
    tags=["codeforces"]
)
app.include_router(
    atcoder_router,
    prefix="/atcoder",
    tags=["atcoder"]
)
app.include_router(
    codechef_router,
    prefix="/codechef",
    tags=["codechef"]
)
app.include_router(leetcode_router)
app.include_router(auth_router)
app.include_router(linked_user_router)
app.include_router(dashboard_router)