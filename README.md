# Movie Ticketing Backend

영화 티켓 발권 및 환불을 처리하는 백엔드 API 서버입니다.

## 기능

- 🎫 티켓 발권 (자유석 기준)
- 💰 티켓 환불
- 🔍 티켓 조회 (단일/목록)
- 🔒 멱등성 지원 (Idempotency-Key)
- 💾 SQLite 기반 영속성

## 기술 스택

- **Framework**: FastAPI
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Server**: Uvicorn

## 설치

```bash
# 의존성 설치
uv sync
```

## 실행

```bash
# 콘솔 스크립트로 실행
uv run movie-ticketing-backend

# 또는 모듈로 직접 실행
uv run python -m movie_ticketing_backend
```

서버는 `http://0.0.0.0:9000`에서 실행됩니다.

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:9000/docs
- **ReDoc**: http://localhost:9000/redoc
- **OpenAPI JSON**: http://localhost:9000/openapi.json

## API 엔드포인트

### 1. 티켓 발권

```http
POST /tickets/issue
Content-Type: application/json
Idempotency-Key: optional-unique-key

{
  "theater_name": "CGV 강남",
  "user_id": "user123",
  "movie_title": "오펜하이머",
  "price_krw": 15000,
  "quantity": 2,
  "memo": "VIP석"
}
```

**응답 (201 Created)**:
```json
{
  "ticket_ids": ["uuid1", "uuid2"],
  "count": 2,
  "summary": {
    "theater_name": "CGV 강남",
    "movie_title": "오펜하이머",
    "price_krw": 15000
  }
}
```

### 2. 티켓 환불

```http
POST /tickets/refund
Content-Type: application/json

{
  "ticket_ids": ["uuid1", "uuid2"],
  "reason": "고객 요청"
}
```

**응답 (200 OK)**:
```json
{
  "refunded": ["uuid1"],
  "already_canceled": ["uuid2"],
  "not_found": []
}
```

### 3. 티켓 단일 조회

```http
GET /tickets/{ticket_id}
```

**응답 (200 OK)**:
```json
{
  "id": "uuid1",
  "theater_name": "CGV 강남",
  "user_id": "user123",
  "movie_title": "오펜하이머",
  "price_krw": 15000,
  "status": "issued",
  "issued_at": "2025-11-15T10:00:00",
  "canceled_at": null,
  "memo": "VIP석"
}
```

### 4. 티켓 목록 조회

```http
GET /tickets?theater_name=CGV%20강남&status=issued&limit=10&offset=0
```

**응답 (200 OK)**:
```json
{
  "tickets": [...],
  "total": 25,
  "limit": 10,
  "offset": 0
}
```

## 프로젝트 구조

```
src/movie_ticketing_backend/
├── __init__.py              # Main entry point
├── app.py                   # FastAPI application factory
├── db/
│   ├── session.py          # Database session and engine
│   └── repository.py       # Ticket CRUD operations
├── entity/
│   └── ticket.py           # SQLAlchemy ORM models
├── scheme/
│   └── ticket.py           # Pydantic request/response schemas
├── service/
│   └── ticket_service.py   # Business logic
├── route/
│   └── ticket_route.py     # API endpoints
└── util/
    └── idempotency.py      # Idempotency utility

data/
└── app.db                   # SQLite database (auto-created)
```

## 데이터베이스

- **위치**: `data/app.db`
- **타입**: SQLite
- **스키마**: 자동 생성 (앱 시작 시)

### Tickets 테이블

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT (PK) | 티켓 고유 ID (UUID) |
| theater_name | TEXT | 극장명 |
| user_id | TEXT | 사용자 ID |
| movie_title | TEXT | 영화 제목 |
| price_krw | INTEGER | 가격 (원) |
| status | TEXT | 상태 (issued/canceled) |
| issued_at | DATETIME | 발권 시각 |
| canceled_at | DATETIME | 환불 시각 (nullable) |
| memo | TEXT | 메모 (nullable) |

## 개발

```bash
# 개발 모드로 실행 (hot reload)
uv run uvicorn movie_ticketing_backend.app:create_app --factory --reload --port 9000

# 코드 포맷팅
uv run black src/

# 타입 체크
uv run mypy src/
```

## 테스트

```bash
# 테스트 실행
uv run pytest

# 커버리지 포함
uv run pytest --cov=movie_ticketing_backend
```

## 문서

- [PRD (Product Requirements Document)](docs/PRD.md)
- [TRD (Technical Requirements Document)](docs/TRD.md)

## 라이선스

MIT

