import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()


# ==============================
# DATABASE CONFIGURATION
# ==============================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set.")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==============================
# FILE UPLOAD CONFIGURATION
# ==============================

UPLOAD_DIRECTORY = os.getenv(
    "UPLOAD_DIRECTORY"
) or "./uploads"

os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
