from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MusicianProfile(Base):
    __tablename__ = "musician_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_musician_profiles_user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_musician_profiles_user_id_users",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    display_name: Mapped[str] = mapped_column(String(120))
    city: Mapped[str] = mapped_column(String(80))
    genres: Mapped[str] = mapped_column(String(255))  # comma-separated for MVP
    instruments: Mapped[str] = mapped_column(String(255))
    years_experience: Mapped[int] = mapped_column(Integer, default=0)
    band_status: Mapped[str] = mapped_column(String(20), default="solo")  # solo | in_band | looking
