from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def placeholder():
    return {"module": "bookings", "status": "stub - implement in roadmap phase"}
