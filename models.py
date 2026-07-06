"""
models.py  -  The SHAPE of the data we demand from the model

"""


from pydantic import BaseModel, Field 


class InterviewQuestion(BaseModel):
    """One interview question, its model answer, and deeper follow-ups."""

    question: str = Field(...,description="A clear interview question.")
    model_answer: str = Field(
        ...,
        description="A strong, complete reference answer a senior candiate would give.",
    )
    follow_ups: list[str] = Field(
        ...,
        description="Two or three deeper follow-up questions an interviewer might ask next."
    )

class QuestionSet(BaseModel):
    """The full set the model returns for a topic."""

    topic: str = Field(..., description="The topic these question cover.")

    questions: list[InterviewQuestion] = Field(
        ...,
        min_length=1,
        description="The list of interview questions for the topic.",
    )