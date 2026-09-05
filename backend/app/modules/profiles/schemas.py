from pydantic import BaseModel


class ProfileCreate(BaseModel):
    display_name: str
    city: str
    genres: list[str] = []
    instruments: list[str] = []
    years_experience: int = 0
    band_status: str = "solo"


class ProfileOut(ProfileCreate):
    id: int

    class Config:
        from_attributes = True
