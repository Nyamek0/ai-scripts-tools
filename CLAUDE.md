# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AITools Platform — a modular, open-source AI tools platform. Backend: FastAPI + Celery + PostgreSQL + Redis. Frontend: Next.js 14 + TypeScript + Tailwind. Documentation and comments are in French.

## Development Commands

### Backend (Docker — recommended)
```bash
cp .env.example .env          # Set SECRET_KEY at minimum
docker compose up --build -d  # Start all services
docker compose logs -f api    # Follow API logs
docker compose restart api    # Reload after code changes
docker compose down -v        # Full reset (deletes DB volumes)
```

### Backend (without Docker)
```bash
# Setup (once)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python scripts/create_superadmin.py

# Run (each in a separate terminal)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
celery -A core.celery_app worker --queues=fast --concurrency=2 --loglevel=info
celery -A core.celery_app worker --queues=slow --concurrency=1 --loglevel=info
celery -A core.celery_app beat --loglevel=info   # optional: scheduled cleanup
celery -A core.celery_app flower --port=5555      # optional: monitoring UI
```

### Database Migrations
```bash
alembic upgrade head                                  # Apply all pending
alembic revision --autogenerate -m "description"     # Generate after model changes
alembic downgrade -1                                  # Rollback one step
alembic history && alembic current                    # Inspect state
```

### Frontend
```bash
cd aitools-frontend
npm install
npm run dev       # Dev server on :3000
npm run build     # Production build
npm run lint      # Next.js lint
```

### Services (running)
- API + Swagger: http://localhost:8000 / http://localhost:8000/docs
- Frontend: http://localhost:3000
- Flower (Celery dashboard): http://localhost:5555
- PostgreSQL: localhost:5432 / Redis: localhost:6379

## Architecture

### Request Flow
1. Next.js frontend → FastAPI backend
2. FastAPI routes to a module via `ModuleRegistry` (auto-discovered at startup)
3. Module router validates input, delegates to service
4. Service either processes synchronously or enqueues a Celery task
5. Client polls `GET /api/{module}/result/{job_id}` until complete
6. Results stored in `outputs/` (local) or S3; files auto-deleted after 24h

### Module Auto-Discovery
`core/module_registry.py` scans `/modules/` at startup. To add a new AI module:
1. Create `modules/{name}/router.py` with `router: APIRouter` and `MODULE_META` dict
2. Optionally add `service.py`, `models.py`, `schemas.py`
3. Router auto-mounts at `/api/{prefix}`

### Celery Task Queues
Two queues configured in `core/celery_app.py`:
- **fast** (concurrency 2): bg_remove, ocr, pdf_merge, convert_image
- **slow** (concurrency 1): transcribe (Whisper), tts, compress_video, summarize

Task timeout: 10 min soft / 11 min hard. Results expire in Redis after 1 hour. JSON serialization only (no pickle).

### Authentication
JWT (HS256) via `core/security.py`. Tokens: 60 min default, 30 days with `remember_me`. Passwords hashed with bcrypt. Auth dependency injected into protected routes via `modules/auth/dependencies.py`.

### File Handling
`core/file_handler.py` is a singleton managing:
- Uploads → `uploads/{subfolder}/{job_id}.ext`
- Outputs → `outputs/{subfolder}/{job_id}.ext`
- Max 50 MB (configurable via `MAX_FILE_SIZE_MB`)
- Celery Beat schedules cleanup of files older than 24h

### Key Files
| File | Purpose |
|------|---------|
| `main.py` | FastAPI app entry, CORS, lifespan hooks, root endpoints |
| `core/config.py` | Pydantic settings — all env vars, limits, paths |
| `core/module_registry.py` | Module auto-discovery and router registration |
| `core/celery_app.py` | Celery config, queue routing |
| `core/file_handler.py` | Upload/output/cleanup logic |
| `modules/auth/` | JWT auth (register, login, me) |
| `modules/jobs/` | Job history and statistics |
| `docker-compose.yml` | 7-service stack (api, worker_fast, worker_slow, beat, flower, redis, postgres) |

### Environment Variables (`.env`)
Critical: `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`. Optional: `STORAGE_BACKEND` (local or s3), `AWS_*` credentials, `UPLOAD_DIR`, `OUTPUT_DIR`.
