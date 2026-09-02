from fastapi import FastAPI

from app.users.route import router as user_router
from app.database import engine
from app.base import Base
from app.users import model

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(user_router)

@app.get("/")
def home():
    return {"message": "Welcome to StudyBuddy AI"}