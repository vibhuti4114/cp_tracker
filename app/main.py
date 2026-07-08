
from fastapi import FastAPI
from app.api.codeforces import router as cf_router
from fastapi.middleware.cors import CORSMiddleware

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