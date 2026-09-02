import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

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


load_dotenv()

app = FastAPI()


# =========================
# CORS
# =========================

# FRONTEND_URL can be a comma-separated list of origins
# for environments that need multiple allowed origins.
# Example: http://localhost:3000,https://yourdomain.com
_frontend_url = os.getenv(
    "FRONTEND_URL",
    "http://localhost:3000"
)

allowed_origins = [
    origin.strip()
    for origin in _frontend_url.split(",")
    if origin.strip()
]

# Always include localhost variants for local development
# only when no production origin has been explicitly set.
if _frontend_url == "http://localhost:3000":
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
