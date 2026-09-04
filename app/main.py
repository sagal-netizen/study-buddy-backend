import os

from dotenv import load_dotenv

# Load environment variables BEFORE importing anything
# that depends on them.
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.base import Base

from app.user.model import User
from app.course.model import Course, Chapter, Material
from app.progress.model import ChapterProgress

from app.user.route import router as user_router
from app.course.route import router as course_router
from app.ai.route import router as ai_router
from app.ai.quiz_route import router as quiz_router
from app.progress.route import router as progress_router


app = FastAPI()


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# DATABASE
# =========================

Base.metadata.create_all(
    bind=engine
)


# =========================
# ROUTERS
# =========================

app.include_router(user_router)
app.include_router(course_router)
app.include_router(ai_router)
app.include_router(quiz_router)
app.include_router(progress_router)


# =========================
# HOME
# =========================

@app.get("/")
def home():
    return {
        "message": "Welcome to StudyBuddy AI"
    }