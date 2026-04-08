from pydantic import BaseModel, Field
from typing import List


class SentimentScores(BaseModel):
    positive: float
    negative: float
    neutral: float
    compound: float


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)


class AnalyzeResponse(BaseModel):
    text: str
    label: str
    confidence: float
    scores: SentimentScores


class BatchAnalyzeRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1, max_length=50)


class BatchAnalyzeResponse(BaseModel):
    results: List[AnalyzeResponse]
    total: int

class HealthResponse(BaseModel):
    status: str
    version: str