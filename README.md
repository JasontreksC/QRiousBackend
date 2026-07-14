# QRiousBackend

FastAPI + PostgreSQL 백엔드 서버입니다. Docker Compose로 앱과 DB를 함께 실행합니다.

## 구성

| 서비스 | 설명 | 포트 |
|--------|------|------|
| `backend` | FastAPI 앱 | `8000` |
| `db` | PostgreSQL 16 | `5432` |

## 빠른 시작

```bash
cp .env.example .env
docker compose up --build -d
```

- API 문서: http://localhost:8000/docs
- Health check: http://localhost:8000/health

종료:

```bash
docker compose down
```

DB 데이터까지 삭제하려면:

```bash
docker compose down -v
```

## DB 스키마

ERD 기준 스키마는 `db/schema.sql`에 정의되어 있으며, PostgreSQL 컨테이너 최초 기동 시 자동 적용됩니다.

- `student` — 신청자 기본 정보
- `charm` — 매력(속성) 마스터
- `have` — 신청자가 가진 매력 (다대다)
- `want` — 신청자의 이상형 매력 (다대다)

## API 개요

| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/students` | 학생 목록 |
| POST | `/api/students` | 학생 생성 |
| GET | `/api/students/{student_id}` | 학생 조회 |
| PATCH | `/api/students/{student_id}` | 학생 수정 |
| DELETE | `/api/students/{student_id}` | 학생 삭제 |
| GET | `/api/charms` | 매력 목록 |
| POST | `/api/charms` | 매력 생성 |
| GET | `/api/charms/{charm_id}` | 매력 조회 |
| PATCH | `/api/charms/{charm_id}` | 매력 수정 |
| DELETE | `/api/charms/{charm_id}` | 매력 삭제 |

## 로컬 개발 (Docker 없이)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# PostgreSQL이 localhost:5432 에서 실행 중이어야 함
export DATABASE_URL=postgresql+psycopg2://qrious:qrious@localhost:5432/qrious
uvicorn app.main:app --reload
```
