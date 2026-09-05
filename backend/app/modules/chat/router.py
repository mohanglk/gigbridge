from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def placeholder():
    return {"module": "chat", "status": "stub - implement in roadmap phase"}
