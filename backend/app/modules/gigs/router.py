from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def placeholder():
    return {"module": "gigs", "status": "stub - implement in roadmap phase"}
