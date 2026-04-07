"""
FastAPI 애플리케이션 진입점.

실행 방법:
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers.sentiment import router as sentiment_router
from app.schemas.sentiment import HealthResponse
from app.services.analyzer import get_analyzer

# ──────────────────────────────────────────────
# 로깅 설정
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

API_VERSION = "v1"


# ──────────────────────────────────────────────
# 애플리케이션 생명주기 (lifespan)
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버 시작 시 VADER 모델을 미리 로드하여 첫 요청 지연을 방지합니다."""
    logger.info("🚀 서버 시작 — VADER 모델 사전 로드 중...")
    get_analyzer()  # 싱글턴 초기화 (lru_cache)
    logger.info("✅ VADER 모델 로드 완료. API 준비 완료.")
    yield
    logger.info("🛑 서버 종료.")


# ──────────────────────────────────────────────
# FastAPI 앱 생성
# ──────────────────────────────────────────────
app = FastAPI(
    title="Sentiment Analysis API",
    description=(
        "## VADER 기반 감성 분석 API\n\n"
        "텍스트를 입력하면 **긍정(positive)**, **부정(negative)**, **중립(neutral)**으로 분류합니다.\n\n"
        "- 단일 텍스트 분석\n"
        "- 배치(최대 50개) 분석\n"
        "- GPU 불필요, 경량 모델\n"
    ),
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ──────────────────────────────────────────────
# CORS 미들웨어
# ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 프로덕션에서는 도메인을 명시하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────
# 요청 처리 시간 로깅 미들웨어
# ──────────────────────────────────────────────
@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s → %d [%.1f ms]",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


# ──────────────────────────────────────────────
# 전역 예외 핸들러
# ──────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("처리되지 않은 예외 발생: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "서버 내부 오류가 발생했습니다. 관리자에게 문의하세요."},
    )


# ──────────────────────────────────────────────
# 라우터 등록
# ──────────────────────────────────────────────
app.include_router(sentiment_router, prefix=f"/api/{API_VERSION}")


# ──────────────────────────────────────────────
# 헬스체크
# ──────────────────────────────────────────────
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="서비스 헬스체크",
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        model="VADER (vaderSentiment)",
        version=API_VERSION,
    )


@app.get("/", tags=["Root"], include_in_schema=False)
async def root():
    return {
        "message": "Sentiment Analysis API가 실행 중입니다.",
        "docs": "/docs",
        "health": "/health",
    }
