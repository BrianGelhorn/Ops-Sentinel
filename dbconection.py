from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

POSTGRES_USER=os.getenv("POSTGRES_USER", "postgres")
POSTGRES_DB=os.getenv("POSTGRES_DB", POSTGRES_USER)
POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD")
PORT=5432
engine = create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:{PORT}/{POSTGRES_DB}")

Session = sessionmaker(bind=engine)
session = Session()

DBaseModel = declarative_base()