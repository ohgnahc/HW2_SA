# ──────────────────────────────────────────────────────────────
# Multi-stage Dockerfile — Sentiment Analysis API
# 최적화 포인트:
#   1. requirements.txt 먼저 COPY → pip 레이어 캐시 최대 활용
#   2. --no-cache-dir 로 pip 캐시 제거 → 이미지 크기 감소
#   3. 런타임에 불필요한 build-essential 제거 (multi-stage)
#   4. Python 최적화 환경변수 설정
#   5. OCI 표준 이미지 레이블
#   6. 비루트 사용자(appuser) 실행 → 보안 강화
# ──────────────────────────────────────────────────────────────

# ── Build Arguments ──────────────────────────────────────────
ARG PYTHON_VERSION=3.11
ARG APP_VERSION=latest

# ── Stage 1: builder — 의존성 컴파일 ──────────────────────────
FROM python:${PYTHON_VERSION}-slim AS builder

WORKDIR /build

# 빌드 도구 설치 (런타임 이미지에는 포함되지 않음)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# ★ requirements.txt를 소스보다 먼저 복사
#   → 소스 변경 시에도 pip 레이어 캐시 재사용 가능
COPY requirements.txt .

RUN pip install --upgrade pip --no-cache-dir \
    && pip install \
        --prefix=/install \
        --no-cache-dir \
        --compile \
        -r requirements.txt


# ── Stage 2: runtime — 최소 실행 환경 ─────────────────────────
FROM python:${PYTHON_VERSION}-slim AS runtime

# ── Python 환경 최적화 ────────────────────────────────────────
# PYTHONDONTWRITEBYTECODE : .pyc 파일 생성 안 함 → 이미지 크기 감소
# PYTHONUNBUFFERED        : stdout/stderr 버퍼링 없이 즉시 출력 → 로그 실시간
# PYTHONFAULTHANDLER      : 세그멀트 폴트 시 파이썬 트레이스백 출력
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    # pip가 버전 경고를 출력하지 않도록
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ── OCI 이미지 레이블 ─────────────────────────────────────────
ARG APP_VERSION
LABEL org.opencontainers.image.title="Sentiment Analysis API" \
      org.opencontainers.image.description="VADER-based sentiment analysis REST API built with FastAPI" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.authors="changho" \
      org.opencontainers.image.source="https://github.com/changho/sentiment-api" \
      org.opencontainers.image.licenses="MIT"

# ── 비루트 사용자 생성 (보안 강화) ───────────────────────────
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup --no-create-home appuser

WORKDIR /app

# Stage 1에서 컴파일된 패키지만 복사 (빌드 도구 제외)
COPY --from=builder /install /usr/local

# 소스 코드 복사 (소유권: appuser)
COPY --chown=appuser:appgroup app/ ./app/

# 비루트 사용자로 전환
USER appuser

EXPOSE 8000

# ── 헬스체크 ─────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c \
        "import urllib.request, sys; \
         r = urllib.request.urlopen('http://localhost:8000/health', timeout=5); \
         sys.exit(0 if r.status == 200 else 1)"

# ── 실행 명령 ─────────────────────────────────────────────────
# --workers 1: 컨테이너 환경에서는 프로세스 수를 제한
#              (수평 확장은 컨테이너 복제로 처리)
# 더 많은 동시 요청이 필요하면 --workers 를 늘리거나
# Gunicorn + uvicorn worker 조합을 사용하세요.
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--access-log"]
