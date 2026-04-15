from fastapi import APIRouter, status
from datetime import datetime
from schemas import *
from crud import create_incident, upload_to_database

router = APIRouter(prefix="/incidents")


#TODO: Implement the SQLConnection
INCIDENTS=[]

@router.get("")
async def get_incidents():
    return INCIDENTS

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def post_incidents(item: CreateItem):
    incident = create_incident(item)
    upload_to_database(incident)
    return item