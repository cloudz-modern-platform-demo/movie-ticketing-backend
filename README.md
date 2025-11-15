# Movie Ticketing Backend

영화 티켓 발권 및 환불 API 백엔드 서비스

## 개요

FastAPI 기반의 영화 티켓팅 백엔드 시스템입니다. 자유석 기준의 간단한 발권 API와 환불 API를 제공하며, SQLite 데이터베이스를 사용하여 데이터를 영속화합니다.

## 주요 기능

- ✅ 티켓 발권 (여러 장 동시 발권 지원)
- ✅ 티켓 환불 (배치 환불 지원)
- ✅ 티켓 단일 조회
- ✅ 티켓 목록 조회 (필터링 및 페이징)
- ✅ 멱등성 지원 (Idempotency-Key 헤더)
- ✅ SQLite 기반 영속화
- ✅ OpenAPI/Swagger 문서 자동 생성

## 기술 스택

- **언어**: Python 3.12+
- **프레임워크**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **데이터베이스**: SQLite
- **검증**: Pydantic 2.0
- **서버**: Uvicorn

## 프로젝트 구조

```
src/movie_ticketing_backend/
├── __init__.py              # 메인 진입점
├── app.py                   # FastAPI 앱 팩토리
├── db/
│   ├── session.py          # 데이터베이스 세션 설정
│   └── repository.py       # 티켓 리포지토리
├── entity/
│   └── ticket.py           # Ticket ORM 엔티티
├── scheme/
│   └── ticket.py           # Pydantic 스키마
├── service/
│   └── ticket_service.py   # 비즈니스 로직
├── route/
│   └── ticket_route.py     # REST API 엔드포인트
└── util/
    └── idempotency.py      # 멱등성 캐시
```

## 설치 및 실행

### 1. 의존성 설치

```bash
# uv 사용 (권장)
uv sync

# 또는 pip 사용
pip install -e .
```

### 2. 서버 실행

```bash
# 콘솔 스크립트로 실행 (권장)
uv run movie-ticketing-backend

# 또는 직접 실행
python -m movie_ticketing_backend
```

서버는 `http://0.0.0.0:9000`에서 실행됩니다.

### 3. API 문서 확인

- Swagger UI: http://localhost:9000/docs
- ReDoc: http://localhost:9000/redoc
- OpenAPI JSON: http://localhost:9000/openapi.json

## API 엔드포인트

### 1. 티켓 발권

**POST** `/tickets/issue`

```bash
curl -X POST "http://localhost:9000/tickets/issue" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: unique-key-123" \
  -d '{
    "theater_name": "CGV 강남",
    "user_id": "user123",
    "movie_title": "영화 제목",
    "price_krw": 15000,
    "quantity": 2,
    "memo": "VIP석"
  }'
```

**응답 (201 Created)**:
```json
{
  "ticket_ids": ["abc123", "def456"],
  "count": 2,
  "summary": {
    "theater_name": "CGV 강남",
    "movie_title": "영화 제목",
    "price_krw": 15000
  }
}
```

### 2. 티켓 환불

**POST** `/tickets/refund`

```bash
curl -X POST "http://localhost:9000/tickets/refund" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_ids": ["abc123", "def456"],
    "reason": "고객 요청"
  }'
```

**응답 (200 OK)**:
```json
{
  "refunded": ["abc123"],
  "already_canceled": ["def456"],
  "not_found": []
}
```

### 3. 티켓 단일 조회

**GET** `/tickets/{ticket_id}`

```bash
curl -X GET "http://localhost:9000/tickets/abc123"
```

**응답 (200 OK)**:
```json
{
  "id": "abc123",
  "theater_name": "CGV 강남",
  "user_id": "user123",
  "movie_title": "영화 제목",
  "price_krw": 15000,
  "status": "issued",
  "memo": "VIP석",
}
```

### 4. 티켓 목록 조회

**GET** `/tickets`

```bash
# 필터링 및 페이징 예시
curl -X GET "http://localhost:9000/tickets?theater_name=CGV%20강남&status=issued&limit=10&offset=0"
```

**응답 (200 OK)**:
```json
{
  "tickets": [
    {
      "id": "abc123",
      "theater_name": "CGV 강남",
      "user_id": "user123",
      "movie_title": "영화 제목",
      "price_krw": 15000,
      "status": "issued",
      "memo": "VIP석",
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

## 데이터베이스

- **타입**: SQLite
- **경로**: `data/app.db`
- **초기화**: 애플리케이션 시작 시 자동으로 테이블 생성

### 티켓 테이블 스키마

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | TEXT (PK) | UUID 형식의 티켓 ID |
| theater_name | TEXT | 극장명 (최대 100자) |
| user_id | TEXT | 사용자 ID (최대 100자) |
| movie_title | TEXT | 영화명 (최대 200자) |
| price_krw | INTEGER | 가격 (KRW, 1~1,000,000) |
| status | TEXT | 상태 (issued \| canceled) |
| memo | TEXT | 메모 (선택) |

## 멱등성 (Idempotency)

동일한 요청의 중복 처리를 방지하기 위해 `Idempotency-Key` 헤더를 지원합니다.

- **헤더**: `Idempotency-Key: <unique-key>`
- **동작**:
  - 동일한 키와 요청 본문: 캐시된 응답 반환 (200 OK)
  - 동일한 키, 다른 요청 본문: 409 Conflict 반환
  - 새로운 키: 정상 처리 후 캐시 저장 (201 Created)

## 상태 코드

| 코드 | 설명 |
|------|------|
| 200 OK | 조회 성공, 환불 성공 |
| 201 Created | 발권 성공 |
| 400 Bad Request | 입력 유효성 오류 |
| 404 Not Found | 티켓이 존재하지 않음 |
| 409 Conflict | 멱등성 키 충돌 |
| 500 Internal Server Error | 서버 내부 오류 |

## 유효성 검증

- **theater_name**: 1~100자
- **user_id**: 1~100자
- **movie_title**: 1~200자
- **price_krw**: 1 ~ 1,000,000 (정수)
- **quantity**: 1 ~ 10 (정수)

## 개발 문서

자세한 개발 문서는 `docs/` 디렉토리를 참조하세요:

- [PRD.md](docs/PRD.md) - 제품 요구사항 문서
- [TRD.md](docs/TRD.md) - 기술 설계 문서

## 라이선스

MIT License
