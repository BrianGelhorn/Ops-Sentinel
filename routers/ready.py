from fastapi import APIRouter

router = APIRouter()

@router.get("/ready")
async def get_ready():
    #TODO: Give funcionality to the ready depending the status of the api and database
    return {"status": "ready"}
