"""
감성 분석 서비스 레이어 (다국어 지원).

- 영어: VADER (초고속, 규칙 기반)
- 한국어/기타 언어: cardiffnlp/twitter-xlm-roberta-base-sentiment (트랜스포머 기반 다국어 모델)
"""

import logging
import re
from functools import lru_cache
from typing import Tuple

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline

from app.schemas.sentiment import AnalyzeResponse, SentimentScores

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# 임계값 및 설정
# ──────────────────────────────────────────────
VADER_POSITIVE_THRESHOLD = 0.05
VADER_NEGATIVE_THRESHOLD = -0.05
TRANSFORMER_MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment"


@lru_cache(maxsize=1)
def get_vader_analyzer() -> SentimentIntensityAnalyzer:
    """싱글턴 VADER 분석기를 반환합니다."""
    logger.info("VADER SentimentIntensityAnalyzer 초기화 중...")
    analyzer = SentimentIntensityAnalyzer()
    logger.info("VADER 초기화 완료.")
    return analyzer


@lru_cache(maxsize=1)
def get_transformer_analyzer():
    """싱글턴 Transformer 파이프라인을 반환합니다."""
    logger.info(f"Transformer 모델 초기화 중: {TRANSFORMER_MODEL}...")
    # top_k=None으로 설정하여 모든 클래스(긍정/부정/중립)의 확률을 반환받습니다.
    analyzer = pipeline("sentiment-analysis", model=TRANSFORMER_MODEL, top_k=None)
    logger.info("Transformer 초기화 완료.")
    return analyzer


def preload_models():
    """앱 기동 시 모든 모델을 메모리에 로드해 둡니다."""
    get_vader_analyzer()
    # Transformer 모델은 무거우므로 기동 시 시간이 꽤 소요됩니다.
    get_transformer_analyzer()


def _is_korean(text: str) -> bool:
    """텍스트에 한글이 포함되어 있는지 확인합니다."""
    return bool(re.search(r'[가-힣ㄱ-ㅎㅏ-ㅣ]', text))


def _vader_scores_to_label(compound: float) -> Tuple[str, float]:
    """VADER compound 점수를 레이블과 신뢰도로 변환합니다."""
    if compound >= VADER_POSITIVE_THRESHOLD:
        label = "positive"
        confidence = round((compound + 1) / 2, 4)
    elif compound <= VADER_NEGATIVE_THRESHOLD:
        label = "negative"
        confidence = round((1 - compound) / 2, 4)
    else:
        label = "neutral"
        confidence = round(1 - abs(compound) / 0.05, 4)
        confidence = max(0.0, min(1.0, confidence))
    return label, confidence


def analyze_vader(text: str) -> AnalyzeResponse:
    """VADER를 사용해 영어 텍스트를 분석합니다."""
    analyzer = get_vader_analyzer()
    raw: dict = analyzer.polarity_scores(text)
    
    compound: float = raw["compound"]
    label, confidence = _vader_scores_to_label(compound)
    
    return AnalyzeResponse(
        text=text,
        label=label,
        confidence=confidence,
        compound_score=round(compound, 4),
        scores=SentimentScores(
            positive=round(raw["pos"], 4),
            negative=round(raw["neg"], 4),
            neutral=round(raw["neu"], 4),
            compound=round(compound, 4),
        ),
    )


def analyze_transformer(text: str) -> AnalyzeResponse:
    """Transformer를 사용해 다국어(한국어) 텍스트를 분석합니다."""
    analyzer = get_transformer_analyzer()
    # 파이프라인 리턴 형태: [[{'label': 'negative', 'score': 0.8}, ...]]
    results = analyzer(text)
    
    # 딕셔너리로 매핑 (카디프 모델의 label 리턴을 소문자로 매핑해서 안전성 확보)
    scores_dict = {item['label'].lower(): item['score'] for item in results[0]}
    
    pos = scores_dict.get('positive', 0.0)
    neg = scores_dict.get('negative', 0.0)
    neu = scores_dict.get('neutral', 0.0)
    
    # Compound 합성 (-1 ~ 1)
    compound = pos - neg
    
    # 가장 높은 점수를 가진 label 도출
    best_label = max(scores_dict, key=scores_dict.get)
    confidence = scores_dict[best_label]
    
    return AnalyzeResponse(
        text=text,
        label=best_label,
        confidence=round(confidence, 4),
        compound_score=round(compound, 4),
        scores=SentimentScores(
            positive=round(pos, 4),
            negative=round(neg, 4),
            neutral=round(neu, 4),
            compound=round(compound, 4),
        ),
    )


def analyze_text(text: str) -> AnalyzeResponse:
    """
    단일 텍스트를 분석합니다. (언어 감지를 통해 분석기 선택)
    """
    if _is_korean(text):
        response = analyze_transformer(text)
        logger.debug("Transformer 분석 완료 | label=%s, compound=%.4f | text=%.60r", response.label, response.compound_score, text)
        return response
    else:
        response = analyze_vader(text)
        logger.debug("VADER 분석 완료 | label=%s, compound=%.4f | text=%.60r", response.label, response.compound_score, text)
        return response


def analyze_batch(texts: list[str]) -> list[AnalyzeResponse]:
    """여러 텍스트를 일괄 분석합니다."""
    return [analyze_text(t) for t in texts]
