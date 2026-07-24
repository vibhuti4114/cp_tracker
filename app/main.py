
from fastapi import FastAPI
from app.api.codeforces import router as cf_router
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.database.database import Base,engine
from app.api.linked_account import router as linked_user_router

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
app.include_router(auth_router)
app.include_router(linked_user_router)