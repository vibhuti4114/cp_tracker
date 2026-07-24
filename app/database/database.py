
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker

DATABASE_URL = "postgresql://postgres:vibhuti%40123@localhost:5432/cp_tracker"

engine =create_engine(DATABASE_URL)

SessionLocal= sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base=declarative_base()