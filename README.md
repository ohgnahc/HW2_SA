<<<<<<< HEAD
# Sentiment Analysis API 🎭

VADER 기반의 경량 감성 분석 FastAPI 서버입니다.
GPU 없이 텍스트를 **긍정(positive)**, **부정(negative)**, **중립(neutral)**으로 분류합니다.

---

## 프로젝트 구조

```
sentiment-api/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI 앱 진입점 & 미들웨어
│   ├── routers/
│   │   ├── __init__.py
│   │   └── sentiment.py         # /api/v1/sentiment 라우터
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── sentiment.py         # Pydantic 요청/응답 모델
│   └── services/
│       ├── __init__.py
│       └── analyzer.py          # VADER 싱글턴 분석 서비스
├── requirements.txt
├── Dockerfile
├── .dockerignore
└── README.md
```

---

## 빠른 시작

### 1. 가상환경 생성 및 의존성 설치

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. 서버 실행

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. API 문서 확인

브라우저에서 열기: http://localhost:8000/docs

---

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 헬스체크 |
| POST | `/api/v1/sentiment/analyze` | 단일 텍스트 분석 |
| POST | `/api/v1/sentiment/analyze/batch` | 배치 분석 (최대 50개) |

### 단일 텍스트 분석 예시

**요청:**
```bash
curl -X POST http://localhost:8000/api/v1/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "I absolutely love this! It works perfectly."}'
```

**응답:**
```json
{
  "text": "I absolutely love this! It works perfectly.",
  "label": "positive",
  "confidence": 0.9705,
  "scores": {
    "positive": 0.5,
    "negative": 0.0,
    "neutral": 0.5,
    "compound": 0.941
  }
}
```

### 배치 분석 예시

```bash
curl -X POST http://localhost:8000/api/v1/sentiment/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Great job!", "This is terrible.", "It is okay."]}'
```

---

## Docker로 실행

```bash
# 이미지 빌드
docker build -t sentiment-api:latest .

# 컨테이너 실행
docker run -d -p 8000:8000 --name sentiment-api sentiment-api:latest

# 로그 확인
docker logs -f sentiment-api
```

---

## VADER 레이블 분류 기준

| compound 점수 | 레이블 |
|---|---|
| ≥ 0.05 | positive |
| ≤ -0.05 | negative |
| -0.05 ~ 0.05 | neutral |

> **참고**: VADER는 영어 텍스트에 최적화되어 있습니다.
> 한국어 텍스트는 정확도가 낮을 수 있습니다.

---

## 기술 스택

- **FastAPI** 0.115 — 고성능 비동기 웹 프레임워크
- **uvicorn** — ASGI 서버
- **vaderSentiment** 3.3.2 — 규칙 기반 감성 분석
- **Pydantic** v2 — 데이터 검증
=======
# HW2_SA
>>>>>>> 84c7a9b355459394fd775ea16f60c0038f06062c
