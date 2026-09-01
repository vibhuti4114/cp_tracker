
from sqlalchemy.orm import Session

from app.models.leetcode import (
    LeetCodeProfile,
    LeetCodeContestHistory
)


def get_leetcode_profile(db: Session, handle: str):
    return db.query(LeetCodeProfile).filter(
        LeetCodeProfile.handle == handle
    ).first()


def insert_leetcode_profile(db: Session, data: dict):

    data = data.copy()
    data.pop("tags", None)

    profile = LeetCodeProfile(**data)

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile


def update_leetcode_profile(
    db: Session,
    profile: LeetCodeProfile,
    data: dict
):

    data = data.copy()
    data.pop("tags", None)

    for key, value in data.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)

    return profile


def get_latest_leetcode_contest(
    db: Session,
    profile_id: int
):

    return db.query(LeetCodeContestHistory).filter(
        LeetCodeContestHistory.leetcode_profile_id == profile_id
    ).order_by(
        LeetCodeContestHistory.contest_time.desc()
    ).first()


def insert_leetcode_contests(
    db: Session,
    contests: list[dict]
):

    if contests:
        db.add_all(
            [LeetCodeContestHistory(**x) for x in contests]
        )

        db.commit()