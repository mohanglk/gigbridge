"""Business logic for musician profiles.

Other modules call functions here — never query musician_profiles directly.
"""
from sqlalchemy.orm import Session

from app.modules.profiles.models import MusicianProfile


def get_profile(db: Session, profile_id: int) -> MusicianProfile | None:
    return db.get(MusicianProfile, profile_id)
