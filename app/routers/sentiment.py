"""
감성 분석 API 라우터.

엔드포인트:
  POST /api/v1/sentiment/analyze       단일 텍스트 분석
  POST /api/v1/sentiment/analyze/batch 배치 텍스트 분석
"""

import logging
from fastapi import APIRouter, HTTPException, status

from app.schemas.sentiment import (
    AnalyzeRequest,
    AnalyzeResponse,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
)
from app.services.analyzer import analyze_text, analyze_batch

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/sentiment",
    tags=["Sentiment Analysis"],
)


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="단일 텍스트 감성 분석",
    description=(
        "텍스트를 입력하면 VADER 모델을 사용해 **긍정(positive)**, "
        "**부정(negative)**, **중립(neutral)** 레이블과 세부 점수를 반환합니다."
    ),
)
async def analyze_single(body: AnalyzeRequest) -> AnalyzeResponse:
    try:
        result = analyze_text(body.text)
        logger.info("단일 분석 완료 | label=%s", result.label)
        return result
    except Exception as exc:
        logger.exception("단일 분석 중 오류 발생")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"분석 중 오류가 발생했습니다: {exc}",
        ) from exc


@router.post(
    "/analyze/batch",
    response_model=BatchAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="배치 텍스트 감성 분석",
    description=(
        "최대 50개의 텍스트를 한꺼번에 분석합니다. "
        "각 텍스트에 대한 레이블과 세부 점수를 리스트로 반환합니다."
    ),
)
async def analyze_batch_endpoint(body: BatchAnalyzeRequest) -> BatchAnalyzeResponse:
    try:
        results = analyze_batch(body.texts)
        logger.info("배치 분석 완료 | 총 %d건", len(results))
        return BatchAnalyzeResponse(results=results, total=len(results))
    except Exception as exc:
        logger.exception("배치 분석 중 오류 발생")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"배치 분석 중 오류가 발생했습니다: {exc}",
        ) from exc
