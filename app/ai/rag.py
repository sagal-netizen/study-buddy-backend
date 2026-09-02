import ollama

from app.database import (
    search_documents,
    OLLAMA_BASE_URL,
    OLLAMA_CHAT_MODEL,
)


def ask_studybuddy(
    question: str,
    number_of_results: int = 5,
    course_id: int | None = None
):

    results = search_documents(
        question,
        number_of_results
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    context = "\n\n".join(documents)

    course_context = ""

    if course_id is not None:
        course_context = f"""
The student is currently studying course ID {course_id}.

Focus your academic explanations on this course
and its learning material when relevant.
"""

    prompt = f"""
You are an AI tutor inside StudyBuddy AI.

You are a normal, friendly conversational tutor.

{course_context}

Your personality is:
Friendly, patient and encouraging.

Your teaching style is:
Step-by-step explanations with simple examples.

Your tone is:
Supportive and conversational.

IMPORTANT BEHAVIOR:

1. If the student asks an academic question and
relevant study material is available, use it.

2. Explain concepts instead of simply copying
the study material.

3. If the student says something casual such as
"hi", "hello", "how are you", or wants normal
conversation, respond naturally.

4. If the question is unrelated to the course,
you may still answer briefly and naturally,
but encourage the student to return to learning
when appropriate.

5. Never say that you cannot answer simply because
the exact sentence is not present in the notes.

6. Do not invent information from the study material.

7. If the uploaded material does not contain enough
information for a course-specific question, clearly
say that the material does not provide enough context
and then give a general explanation if you can.

STUDY MATERIAL:
{context}

STUDENT QUESTION:
{question}

Give a helpful response.
"""

    try:
        ollama_client = ollama.Client(
            host=OLLAMA_BASE_URL
        )

        response = ollama_client.chat(
            model=OLLAMA_CHAT_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = response["message"]["content"]

    except Exception as error:

        print("Ollama error:", error)

        answer = (
            "I'm having trouble connecting to my AI "
            "tutor right now. Please try again."
        )

    return {
        "answer": answer,
        "sources": documents
    }
