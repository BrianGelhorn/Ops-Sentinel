from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def get_health():
    return {"status": "alive"}

@app.get("/ready")
async def get_ready():
    #TODO: Give funcionality to the ready depending the status of the api
    return {"status": "ready"}

@app.get("/incidents")
async def get_incidents():
    #TODO: Implement the SQLConnection
    #TODO: Define the structure on the incidents
    return [{"id": 1}, {"id": 2}]