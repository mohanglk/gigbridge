from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MusicianProfile(Base):
    __tablename__ = "musician_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    display_name: Mapped[str] = mapped_column(String(120))
    city: Mapped[str] = mapped_column(String(80))
    genres: Mapped[str] = mapped_column(String(255))  # comma-separated for MVP
    instruments: Mapped[str] = mapped_column(String(255))
    years_experience: Mapped[int] = mapped_column(Integer, default=0)
    band_status: Mapped[str] = mapped_column(String(20), default="solo")  # solo | in_band | looking
