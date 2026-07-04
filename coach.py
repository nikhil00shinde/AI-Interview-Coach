"""
coach.py - The brain of the app: prompts, the validate-and-retry loop, and grading.

generate_questions() -> STRUCTURED OUTPUT + VALIDATE-AND-RETRY. We ask for JSON, parse it against out schema, and if it's malformed we hand the error back to the model

generate_answer() -> STREAMING + PROMPT CRAFT FOR SPECIFICITY. Feedback streams in token by token, and the prompt is written to force SPECIFIC critique instead of empty praise.
"""

from pydantic import ValidationError 

from llm import stream_chat 
from models import QuestionSet 


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
