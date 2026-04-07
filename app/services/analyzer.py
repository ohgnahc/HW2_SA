"""
VADER 기반 감성 분석 서비스 레이어.

SentimentIntensityAnalyzer를 싱글턴으로 관리하여
매 요청마다 재초기화되는 오버헤드를 방지합니다.
"""

import logging
from functools import lru_cache
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from app.schemas.sentiment import AnalyzeResponse, SentimentScores

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# 임계값 설정 (VADER 권장 기준)
# compound >= 0.05  → positive
# compound <= -0.05 → negative
# 그 외             → neutral
# ──────────────────────────────────────────────
POSITIVE_THRESHOLD = 0.05
NEGATIVE_THRESHOLD = -0.05


@lru_cache(maxsize=1)
def get_analyzer() -> SentimentIntensityAnalyzer:
    """싱글턴 VADER 분석기를 반환합니다."""
    logger.info("VADER SentimentIntensityAnalyzer 초기화 중...")
    analyzer = SentimentIntensityAnalyzer()
    logger.info("VADER 초기화 완료.")
    return analyzer


def _scores_to_label(compound: float) -> tuple[str, float]:
    """
    compound 점수를 레이블과 신뢰도로 변환합니다.

    Returns:
        (label, confidence) 튜플
    """
    if compound >= POSITIVE_THRESHOLD:
        label = "positive"
        confidence = round((compound + 1) / 2, 4)  # [-1,1] → [0,1] 정규화
    elif compound <= NEGATIVE_THRESHOLD:
        label = "negative"
        confidence = round((1 - compound) / 2, 4)
    else:
        label = "neutral"
        # 중립은 compound가 0에 가까울수록 신뢰도가 높음
        confidence = round(1 - abs(compound) / 0.05, 4)
        confidence = max(0.0, min(1.0, confidence))

    return label, confidence


def analyze_text(text: str) -> AnalyzeResponse:
    """
    단일 텍스트를 분석합니다.

    Args:
        text: 분석할 원문 텍스트

    Returns:
        AnalyzeResponse 객체
    """
    analyzer = get_analyzer()
    raw: dict = analyzer.polarity_scores(text)

    compound: float = raw["compound"]
    label, confidence = _scores_to_label(compound)

    logger.debug("분석 완료 | label=%s, compound=%.4f | text=%.60r", label, compound, text)

    return AnalyzeResponse(
        text=text,
        label=label,
        confidence=confidence,
        scores=SentimentScores(
            positive=round(raw["pos"], 4),
            negative=round(raw["neg"], 4),
            neutral=round(raw["neu"], 4),
            compound=round(compound, 4),
        ),
    )


def analyze_batch(texts: list[str]) -> list[AnalyzeResponse]:
    """
    여러 텍스트를 일괄 분석합니다.

    Args:
        texts: 분석할 텍스트 목록

    Returns:
        AnalyzeResponse 리스트
    """
    return [analyze_text(t) for t in texts]
