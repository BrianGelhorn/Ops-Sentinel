from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", POSTGRES_USER)
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
PORT = os.getenv("DB_PORT", "5432")
DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{PORT}/{POSTGRES_DB}"
)
engine = create_engine(DATABASE_URL)


Session = sessionmaker(bind=engine)

DBaseModel = declarative_base()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
