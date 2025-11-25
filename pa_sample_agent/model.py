from pydantic import BaseModel
from typing import Literal


class QuestionRequest(BaseModel):
    type: Literal["question"] = "question"
    prompt: str


class StatusRequest(BaseModel):
    type: Literal["status"] = "status"


class AnswerResponse(BaseModel):
    type: Literal["answer"] = "answer"
    answer: str
