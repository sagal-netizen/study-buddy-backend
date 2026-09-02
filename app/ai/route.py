from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.ai.rag import ask_studybuddy
from app.security import get_current_user


router = APIRouter()


class AskRequest(BaseModel):
    question: str
    course_id: int | None = None


@router.post("/ai/ask")
def ask_ai(
    request: AskRequest,
    _current_user: dict = Depends(get_current_user)
):
    if not request.question.strip():
        return {
            "answer": "Please enter a question.",
            "sources": []
        }

    return ask_studybuddy(
        request.question,
        course_id=request.course_id
    )
