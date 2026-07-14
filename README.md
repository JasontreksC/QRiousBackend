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
- Admin UI (SQLAdmin): http://localhost:8000/admin
- Health check: http://localhost:8000/health

Admin 로그인은 `.env`의 `ADMIN_USERNAME` / `ADMIN_PASSWORD` 입니다. 배포 환경에서는 반드시 변경하세요.

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
- `ex_have` — 추가 어필 자유 텍스트 (1:1)
- `ex_want` — 추가 이상형 자유 텍스트 (1:1)

기존 DB에는 `db/migrate_ex_tables.sql`을 실행하세요.

## API 개요

계약서: [`API.md`](API.md)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/charms` | 매력 태그 마스터 목록 |
| GET | `/api/stats` | 성별 참여 현황 통계 |
| POST | `/api/surveys` | 사전조사 일괄 제출 |
| — | `/admin` | SQLAdmin (테이블 CRUD UI) |

## 로컬 개발 (Docker 없이)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# PostgreSQL이 localhost:5432 에서 실행 중이어야 함
export DATABASE_URL=postgresql+psycopg2://qrious:qrious@localhost:5432/qrious
uvicorn app.main:app --reload
```
