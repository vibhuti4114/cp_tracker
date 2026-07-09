
from app.database.database import Base,engine
from app.models.cf_profile import CachedProfile

Base.metadata.create_all(bind=engine)

print("Database Initialized Successfully!")