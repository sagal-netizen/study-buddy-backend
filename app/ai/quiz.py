import json
import os
import random

from mistralai.client import Mistral


# =========================
# MISTRAL CONFIGURATION
# =========================

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    raise RuntimeError(
        "MISTRAL_API_KEY environment variable is not set."
    )

mistral_client = Mistral(
    api_key=MISTRAL_API_KEY
)

MODEL = "mistral-small-latest"


def generate_quiz(
    topic: str,
    number_of_questions: int = 5,
    difficulty: str = "medium"
):

    topic = topic.strip()

    if not topic:

        return {
            "questions": []
        }


    # --------------------------------------------------------
    # CREATE A BALANCED ANSWER PATTERN
    # --------------------------------------------------------

    answer_positions = (
        list(range(4))
        * ((number_of_questions // 4) + 1)
    )[:number_of_questions]

    random.shuffle(
        answer_positions
    )


    # --------------------------------------------------------
    # QUIZ PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are Lyra, the AI quiz tutor inside StudyBuddy AI.

Create a high-quality multiple-choice quiz.

TOPIC:
{topic}

DIFFICULTY:
{difficulty}

NUMBER OF QUESTIONS:
{number_of_questions}

VERY IMPORTANT ANSWER DISTRIBUTION RULE:

The correct answer positions MUST be distributed
across A, B, C and D.

Do NOT make all correct answers option A.

Do NOT make all correct answers option B.

Do NOT use the same answer position repeatedly
when another position is available.

The intended correct-answer positions are:

{answer_positions}

The positions are zero-based:

0 = A
1 = B
2 = C
3 = D

For each question, make the correct option match
the corresponding intended answer position.

Example:

If the intended answer position is 2:

"options": [
    "Wrong answer",
    "Wrong answer",
    "Correct answer",
    "Wrong answer"
],
"answer": 2

The correct answer must genuinely be correct.
Do not simply move the correct answer to satisfy
the position requirement.

OTHER RULES:

1. Create exactly {number_of_questions} questions.

2. Every question must have exactly four options.

3. There must be exactly one correct answer.

4. Questions should test understanding, not only
memorization.

5. Avoid ambiguous questions.

6. Give a short explanation for every answer.

7. Do not use markdown.

8. Return ONLY valid JSON.

Use exactly this structure:

{{
  "questions": [
    {{
      "question": "Question text",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "answer": 0,
      "explanation": "Short explanation."
    }}
  ]
}}

Remember:

The answer value must match the actual correct
option AND the requested answer position.
"""


    # --------------------------------------------------------
    # CALL MISTRAL
    # --------------------------------------------------------

    try:

        response = mistral_client.chat.complete(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = (
            response.choices[0]
            .message.content
            .strip()
        )


        # ----------------------------------------------------
        # REMOVE MARKDOWN CODE FENCES
        # ----------------------------------------------------

        if content.startswith("```"):

            content = content.replace(
                "```json",
                ""
            )

            content = content.replace(
                "```",
                ""
            )

            content = content.strip()


        # ----------------------------------------------------
        # PARSE JSON
        # ----------------------------------------------------

        data = json.loads(
            content
        )

        questions = data.get(
            "questions",
            []
        )


        # ----------------------------------------------------
        # VALIDATE QUESTIONS
        # ----------------------------------------------------

        valid_questions = []

        for item in questions:

            if not isinstance(
                item,
                dict
            ):
                continue

            question_text = item.get(
                "question"
            )

            options = item.get(
                "options",
                []
            )

            answer = item.get(
                "answer"
            )

            explanation = item.get(
                "explanation",
                ""
            )

            if not question_text:
                continue

            if not isinstance(
                options,
                list
            ):
                continue

            if len(options) != 4:
                continue

            if not isinstance(
                answer,
                int
            ):
                continue

            if answer < 0 or answer > 3:
                continue

            valid_questions.append(
                {
                    "question": question_text,
                    "options": options,
                    "answer": answer,
                    "explanation": explanation
                }
            )


        # ----------------------------------------------------
        # IF MODEL RETURNED TOO FEW QUESTIONS
        # ----------------------------------------------------

        if len(valid_questions) == 0:

            return {
                "questions": []
            }


        # ----------------------------------------------------
        # FINAL ANSWER-POSITION CORRECTION
        # ----------------------------------------------------

        final_questions = []

        for index, question in enumerate(
            valid_questions
        ):

            options = list(
                question["options"]
            )

            correct_index = question[
                "answer"
            ]

            if (
                correct_index < 0
                or correct_index >= len(options)
            ):
                continue

            correct_answer = options[
                correct_index
            ]

            remaining_options = [
                option
                for option_index, option
                in enumerate(options)
                if option_index != correct_index
            ]

            desired_position = (
                answer_positions[
                    index
                    % len(answer_positions)
                ]
            )

            random.shuffle(
                remaining_options
            )

            new_options = []

            incorrect_index = 0

            for position in range(4):

                if position == desired_position:

                    new_options.append(
                        correct_answer
                    )

                else:

                    new_options.append(
                        remaining_options[
                            incorrect_index
                        ]
                    )

                    incorrect_index += 1

            final_questions.append(
                {
                    "question":
                        question["question"],

                    "options":
                        new_options,

                    "answer":
                        desired_position,

                    "explanation":
                        question[
                            "explanation"
                        ]
                }
            )


        # ----------------------------------------------------
        # RETURN FINAL QUIZ
        # ----------------------------------------------------

        return {
            "questions":
                final_questions[
                    :number_of_questions
                ]
        }


    except Exception as error:

        print(
            "QUIZ GENERATION ERROR:",
            error
        )

        return {
            "questions": []
        }