from pydantic import BaseModel, Field
from typing import List


# ?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�
# Request Schemas
# ?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�

class AnalyzeRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="분석???�스??(1~5000??",
        examples=["I love this product! It's absolutely amazing."],
    )


class BatchAnalyzeRequest(BaseModel):
    texts: List[str] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="분석???�스??목록 (최�? 50�?",
        examples=[["Great job!", "This is terrible.", "It's okay I guess."]],
    )


# ?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�
# Response Schemas
# ?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�?�

class SentimentScores(BaseModel):
    positive: float = Field(..., ge=0.0, le=1.0, description="긍정 ?�수 (0~1)")
    negative: float = Field(..., ge=0.0, le=1.0, description="부???�수 (0~1)")
    neutral: float = Field(..., ge=0.0, le=1.0, description="중립 ?�수 (0~1)")
    compound: float = Field(..., ge=-1.0, le=1.0, description="복합 ?�수 (-1~1)")


class AnalyzeResponse(BaseModel):
    text: str = Field(..., description="?�력???�문 ?�스??)
    label: str = Field(..., description="감성 ?�이�? positive | negative | neutral")
    confidence: float = Field(..., ge=0.0, le=1.0, description="?�이�??�뢰??(0~1)")
    scores: SentimentScores = Field(..., description="VADER ?��? ?�수")


class BatchAnalyzeResponse(BaseModel):
    results: List[AnalyzeResponse] = Field(..., description="�??�스?�의 분석 결과 목록")
    total: int = Field(..., description="분석???�스????)


class HealthResponse(BaseModel):
    status: str = Field(..., description="?�비???�태")
    model: str = Field(..., description="?�용 중인 모델")
    version: str = Field(..., description="API 버전")
