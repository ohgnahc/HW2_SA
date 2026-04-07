from pydantic import BaseModel, Field
from typing import List


# ──────────────────────────────────────────────
# Request Schemas
# ──────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="분석할 텍스트 (1~5000자)",
        examples=["I love this product! It's absolutely amazing."],
    )


class BatchAnalyzeRequest(BaseModel):
    texts: List[str] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="분석할 텍스트 목록 (최대 50개)",
        examples=[["Great job!", "This is terrible.", "It's okay I guess."]],
    )


# ──────────────────────────────────────────────
# Response Schemas
# ──────────────────────────────────────────────

class SentimentScores(BaseModel):
    positive: float = Field(..., ge=0.0, le=1.0, description="긍정 점수 (0~1)")
    negative: float = Field(..., ge=0.0, le=1.0, description="부정 점수 (0~1)")
    neutral: float = Field(..., ge=0.0, le=1.0, description="중립 점수 (0~1)")
    compound: float = Field(..., ge=-1.0, le=1.0, description="복합 점수 (-1~1)")


class AnalyzeResponse(BaseModel):
    text: str = Field(..., description="입력된 원문 텍스트")
    label: str = Field(..., description="감성 레이블: positive | negative | neutral")
    confidence: float = Field(..., ge=0.0, le=1.0, description="레이블 신뢰도 (0~1)")
    scores: SentimentScores = Field(..., description="VADER 세부 점수")


class BatchAnalyzeResponse(BaseModel):
    results: List[AnalyzeResponse] = Field(..., description="각 텍스트의 분석 결과 목록")
    total: int = Field(..., description="분석된 텍스트 수")


class HealthResponse(BaseModel):
    status: str = Field(..., description="서비스 상태")
    model: str = Field(..., description="사용 중인 모델")
    version: str = Field(..., description="API 버전")
