"""
coach.py  —  The brain of the app: prompts, the validate-and-retry loop, and grading.

Two responsibilities, each teaching a distinct P1 concept:

  generate_questions()  -> STRUCTURED OUTPUT + VALIDATE-AND-RETRY (P1 section 10)
                           We ask for JSON, parse it against our schema, and if
                           it's malformed we hand the error back to the model and
                           ask again. This is what turns an unreliable component
                           into a dependable one.

  grade_answer()        -> STREAMING + PROMPT CRAFT FOR SPECIFICITY (P1 sections 9, 11)
                           Feedback streams in token by token, and the prompt is
                           written to force SPECIFIC critique instead of empty praise.
"""

from pydantic import ValidationError

from llm import stream_chat
from models import QuestionSet


# --- Prompt 1: generate questions -----------------------------------------
# Notice the structure of this prompt:
#   - It sets a persona and rules (this goes in the SYSTEM role).
#   - It SHOWS the exact JSON shape (cheaper and more reliable than describing it).
#   - It is explicit about "no markdown, no prose" because models love to wrap
#     JSON in ```json fences, which then break naive parsing.
QUESTION_SYSTEM_PROMPT = """You are a rigorous, fair technical interviewer.

Given a topic, produce EXACTLY 5 interview questions that escalate in difficulty
(from a warm-up to a genuinely hard one). For each question, also write a strong
model answer and two or three deeper follow-up questions.

Return ONLY valid JSON. No commentary, no markdown code fences. Use this exact shape:

{
  "topic": "<the topic>",
  "questions": [
    {
      "question": "<the question text>",
      "model_answer": "<a strong, complete reference answer>",
      "follow_ups": ["<deeper follow-up>", "<deeper follow-up>"]
    }
  ]
}
"""


def _extract_json(text: str) -> str:
    """
    Pull the JSON object out of the model's reply.

    Models sometimes wrap JSON in prose or ```json fences. Rather than fight
    every variation, we grab everything from the first '{' to the last '}'.
    Simple and robust for our purposes.
    """
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return text.strip()
    return text[start : end + 1]


def generate_questions(topic: str, temperature: float = 0.7, max_retries: int = 3) -> QuestionSet:
    """
    Ask the model for a structured set of interview questions, and refuse to
    return anything that doesn't match our schema.

    The retry loop is the most important engineering in this whole project:
    it's the difference between "works once in a demo" and "works on every run."
    """
    messages = [
        {"role": "system", "content": QUESTION_SYSTEM_PROMPT},
        {"role": "user", "content": f"Topic: {topic}"},
    ]

    last_error = None
    for attempt in range(1, max_retries + 1):
        # show=False: we don't want to print raw streaming JSON to the user —
        # we collect it silently, then parse and present it nicely.
        raw = stream_chat(messages, temperature=temperature, show=False)
        candidate = _extract_json(raw)

        try:
            # model_validate_json parses the string AND checks it against the
            # schema in one step. If anything is missing or the wrong type,
            # it raises ValidationError.
            return QuestionSet.model_validate_json(candidate)
        except ValidationError as error:
            last_error = error
            # Hand the failure back to the model so it can self-correct. We add
            # its broken reply and a correction request to the conversation —
            # the model now SEES what went wrong (P1 section 10).
            messages.append({"role": "assistant", "content": raw})
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Your previous reply did not match the required JSON schema.\n"
                        f"The validation error was:\n{error}\n\n"
                        "Return ONLY corrected JSON matching the schema exactly. "
                        "No prose, no markdown fences."
                    ),
                }
            )
            print(f"  [retry {attempt}/{max_retries}: output was invalid, asking the model to fix it]")

    raise RuntimeError(
        f"The model failed to return valid JSON after {max_retries} attempts.\n"
        f"Last validation error:\n{last_error}"
    )


# --- Prompt 2: grade the candidate's answer --------------------------------
# This prompt is engineered to AVOID the failure mode of generic praise. Read
# how hard it works to demand specificity — that's the lesson. Try weakening it
# (just "Give feedback on the answer.") and watch the quality collapse.
GRADE_SYSTEM_PROMPT = """You are a sharp but supportive interview coach grading a candidate's answer.

Be SPECIFIC and honest. Never give empty praise like "good job" — if something
was good, say exactly which point was good and why. If something was missing or
wrong, name it precisely by comparing to the reference answer.

Give your feedback in this order, briefly:
  1. A score out of 10.
  2. What the candidate got right (concrete points they actually made).
  3. What was missing or incorrect (specific gaps vs. the reference answer).
  4. One concrete, actionable tip to improve.

Keep it tight — a few short paragraphs, not an essay."""


def grade_answer(question: str, model_answer: str, user_answer: str, temperature: float = 0.4) -> str:
    """
    Stream specific, comparative feedback on the candidate's answer.

    We use a lower temperature here (0.4) than for question generation: grading
    should be consistent and grounded, not creative. Feel free to change it and
    see what happens.
    """
    messages = [
        {"role": "system", "content": GRADE_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"QUESTION:\n{question}\n\n"
                f"REFERENCE ANSWER (for your comparison only):\n{model_answer}\n\n"
                f"CANDIDATE'S ANSWER:\n{user_answer}\n\n"
                "Grade the candidate's answer."
            ),
        },
    ]
    # show=True: the feedback streams to the terminal token by token, so the
    # user watches the coach "think" in real time.
    return stream_chat(messages, temperature=temperature, show=True)