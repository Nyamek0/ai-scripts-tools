# AITools Platform

A modular, open-source platform of AI tools behind a single API: background removal, speech-to-text, OCR, text-to-speech, video compression and more. Heavy jobs run asynchronously on Celery workers, and new tools plug in by dropping a folder into `modules/`.

**Stack:** FastAPI · Celery + Redis · PostgreSQL (SQLAlchemy async, Alembic) · Next.js 14 · Docker Compose

## Features

| Module | Library | Input | Output |
|---|---|---|---|
| Background removal | rembg | Image | Transparent PNG |
| Audio transcription | OpenAI Whisper | Audio | TXT / SRT / JSON |
| OCR | EasyOCR | Image | Plain text |
| PDF merge | pypdf | 2–20 PDFs | PDF |
| Text-to-speech | edge-tts | Text (5,000 chars) | MP3 |
| Video compression | ffmpeg | Video | MP4 |
| Text summarization | sumy + nltk | Text (50,000 chars) | Summary |
| Image conversion | Pillow | Image | JPEG / PNG / WebP / BMP / TIFF |

Also included: JWT authentication (register, login, "remember me"), per-user job history, public module statistics, an admin dashboard (platform stats, all jobs), rate limiting, and Flower for monitoring the Celery queues.

## Architecture

```
Next.js frontend ──▶ FastAPI (main.py) ──▶ PostgreSQL   (users, jobs)
                         │
                         └──▶ Redis ──▶ Celery workers
                                         ├─ fast queue  (OCR, convert, PDF…)
                                         └─ slow queue  (Whisper, video…)
```

- `core/` — settings, database, security (JWT + bcrypt), Celery app, file handling, rate limiting, module registry.
- `modules/<name>/` — one folder per tool (`router.py` + `service.py`). Modules are auto-discovered at startup.
- `alembic/` — database migrations.
- `aitools-frontend/` — Next.js 14 app (App Router), FR/EN language toggle, light/dark theme.

## Quick start (Docker)

Requirements: Docker Desktop 24+, Node.js 20+.

```bash
git clone https://github.com/Nyamek0/ai-scripts-tools
cd ai-scripts-tools
cp .env.example .env        # set SECRET_KEY to a long random value

docker compose up --build   # API + workers + Redis + PostgreSQL + Flower
```

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| Swagger docs | http://localhost:8000/docs |
| Flower (Celery) | http://localhost:5555 |

Create the admin account (once). The script asks for the email and password; it never stores credentials in the code:

```bash
docker compose exec api python scripts/create_superadmin.py
```

Start the frontend:

```bash
cd aitools-frontend
npm install
npm run dev                 # http://localhost:3000
```

## Run without Docker

Requires Python 3.11+, ffmpeg, PostgreSQL and Redis running locally.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python scripts/create_superadmin.py

uvicorn main:app --reload --port 8000                                    # API
celery -A core.celery_app worker --queues=fast --concurrency=2 --loglevel=info   # fast tasks
celery -A core.celery_app worker --queues=slow --concurrency=1 --loglevel=info   # Whisper, video
```

## API overview

| Area | Endpoints |
|---|---|
| Health | `GET /health`, `GET /api/modules` |
| Auth | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me` |
| Tools | `POST /api/<module>/process`, `GET /api/<module>/result/{job_id}` |
| Jobs | `GET /api/jobs/mine`, `GET /api/jobs/stats/modules`, admin: `GET /api/jobs/stats/platform`, `GET /api/jobs/all` |

Full interactive documentation at `/docs`.

## Add a new module

Create `modules/my_tool/` with two files:

```python
# router.py
from fastapi import APIRouter
router = APIRouter()

MODULE_META = {
    "name": "My tool",
    "description": "Short description",
    "version": "1.0.0",
    "prefix": "/my-tool",
    "tags": ["my-tool"],
}

@router.post("/process")
async def process():
    ...
```

`service.py` holds the business logic. Restart the API and the module is registered automatically.

## Configuration

Copy `.env.example` to `.env`. The essentials:

```env
SECRET_KEY=change-me-use-openssl-rand-hex-32   # required in production
DATABASE_URL=postgresql://aitools:aitools@localhost:5432/aitools
REDIS_URL=redis://localhost:6379/0
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
MAX_FILE_SIZE_MB=50
ALLOWED_ORIGINS=["http://localhost:3000"]
```

The database credentials above are local development defaults only. Change them for any deployed instance.

## Author

Kokouvi Nyameko Agbodjavou — [github.com/Nyamek0](https://github.com/Nyamek0)
