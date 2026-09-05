from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_profiles():
    return {"todo": "list musician profiles with filters (city, genre, band_status)"}


@router.post("/")
def create_profile():
    return {"todo": "create musician profile"}
