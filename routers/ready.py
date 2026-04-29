from fastapi import APIRouter

router = APIRouter()


@router.get("/ready")
async def get_ready():
    # TODO: Give funcionality to the ready
    return {"status": "ready"}
