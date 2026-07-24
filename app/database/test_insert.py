
from app.database.database import SessionLocal
from app.models.cf_profile import CachedProfile

db=SessionLocal()

profile = CachedProfile(
    handle="tourist",
    rank="legendary grandmaster",
    rating=3850,
    max_rating=4009
)

db.add(profile)
db.commit()

print("Inserted Successfully!")

db.close()