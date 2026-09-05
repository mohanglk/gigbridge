from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def placeholder():
    return {"module": "bands", "status": "stub - implement in roadmap phase"}
