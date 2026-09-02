from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.ai.quiz import generate_quiz
from app.security import get_current_user


router = APIRouter()


class QuizRequest(BaseModel):
    topic: str
    number_of_questions: int = 5
    difficulty: str = "medium"


@router.post("/ai/quiz")
def create_quiz(
    request: QuizRequest,
    _current_user: dict = Depends(get_current_user)
):
    if not request.topic.strip():
        return {
            "questions": []
        }

    return generate_quiz(
        request.topic,
        request.number_of_questions,
        request.difficulty
    )
