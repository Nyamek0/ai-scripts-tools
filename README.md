# AITools Platform

> Plateforme d'outils IA open-source, gratuite, modulaire.
> Stack : FastAPI + Next.js 14 + PostgreSQL + Redis + Celery + Docker

---

## Table des matières

1. [Prérequis](#prérequis)
2. [Structure du projet](#structure-du-projet)
3. [Lancement avec Docker (recommandé)](#lancement-avec-docker-recommandé)
4. [Lancement en développement (sans Docker)](#lancement-en-développement-sans-docker)
5. [Créer le super-admin](#créer-le-super-admin)
6. [Migrations Alembic](#migrations-alembic)
7. [Endpoints disponibles](#endpoints-disponibles)
8. [Modules disponibles](#modules-disponibles)
9. [Ajouter un nouveau module](#ajouter-un-nouveau-module)
10. [Variables d'environnement](#variables-denvironnement)

---

## Prérequis

| Outil | Version minimum | Installation |
|-------|----------------|--------------|
| Docker Desktop | 24+ | https://www.docker.com/products/docker-desktop |
| Node.js | 20+ | https://nodejs.org ou `brew install node` |
| Python | 3.11+ | https://python.org ou `brew install python` |
| ffmpeg | Toute version | `brew install ffmpeg` / `apt install ffmpeg` |
| Git | Toute version | https://git-scm.com |

---

## Structure du projet

```
aitools-platform/
├── main.py                        ← API FastAPI (point d'entrée)
├── core/
│   ├── config.py                  ← Settings (.env)
│   ├── database.py                ← SQLAlchemy async
│   ├── security.py                ← JWT + bcrypt
│   ├── celery_app.py              ← Celery + Redis
│   ├── file_handler.py            ← Upload / nettoyage fichiers
│   ├── module_registry.py         ← Auto-découverte modules
│   └── schemas.py                 ← Modèles Pydantic partagés
├── modules/
│   ├── auth/                      ← Authentification JWT
│   ├── jobs/                      ← Historique & stats
│   ├── bg_remove/                 ← Suppression de fond
│   ├── transcribe/                ← Transcription audio (Whisper)
│   ├── ocr/                       ← OCR image → texte
│   ├── pdf_merge/                 ← Fusion PDF
│   ├── tts/                       ← Synthèse vocale
│   ├── compress_video/            ← Compression vidéo
│   ├── summarize/                 ← Résumé de texte
│   └── convert_image/             ← Conversion d'image
├── alembic/                       ← Migrations base de données
├── scripts/
│   └── create_superadmin.py       ← Créer le compte admin
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── aitools-frontend/              ← Frontend Next.js 14
    ├── src/
    │   ├── app/                   ← Pages (App Router)
    │   ├── components/            ← Composants React
    │   └── lib/                   ← API client, auth, config
    ├── package.json
    └── .env.local
```

---

## Lancement avec Docker (recommandé)

La méthode la plus simple : tout le backend (API + workers + Redis + PostgreSQL) démarre en une commande.

### Étape 1 — Cloner et configurer

```bash
git clone https://github.com/votre-user/aitools-platform
cd aitools-platform

# Copier le fichier de config
cp .env.example .env
```

Éditer `.env` et changer au minimum :
```env
SECRET_KEY=une-cle-secrete-longue-et-aleatoire
```

### Étape 2 — Lancer le backend

```bash
# Démarrer tous les services (API + workers + Redis + PostgreSQL)
docker compose up --build

# Ou en arrière-plan
docker compose up --build -d
```

Services disponibles :
| Service | URL |
|---------|-----|
| API FastAPI | http://localhost:8000 |
| Documentation Swagger | http://localhost:8000/docs |
| Flower (monitoring Celery) | http://localhost:5555 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

### Étape 3 — Créer le super-admin

Dans un nouveau terminal, **une seule fois** :

```bash
docker compose exec api python scripts/create_superadmin.py
```

### Étape 4 — Lancer le frontend

```bash
cd aitools-frontend

# Installer les dépendances (première fois uniquement)
npm install

# Démarrer le serveur de développement
npm run dev
```

Frontend disponible sur : http://localhost:3000

---

## Lancement en développement (sans Docker)

Pour les développeurs qui préfèrent travailler sans Docker.

### Prérequis supplémentaires

- PostgreSQL installé et en cours d'exécution
- Redis installé et en cours d'exécution

```bash
# macOS
brew install postgresql redis
brew services start postgresql
brew services start redis

# Ubuntu/Debian
sudo apt install postgresql redis-server
sudo systemctl start postgresql redis
```

### Étape 1 — Backend Python

```bash
# Créer et activer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos paramètres locaux
```

### Étape 2 — Base de données

```bash
# Appliquer les migrations (crée les tables)
alembic upgrade head

# Créer le super-admin
python scripts/create_superadmin.py
```

### Étape 3 — Lancer les services

Ouvrir **4 terminaux** :

**Terminal 1 — API FastAPI**
```bash
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Worker Celery (tâches rapides)**
```bash
source .venv/bin/activate
celery -A core.celery_app worker --queues=fast --concurrency=2 --loglevel=info
```

**Terminal 3 — Worker Celery (tâches lentes : Whisper…)**
```bash
source .venv/bin/activate
celery -A core.celery_app worker --queues=slow --concurrency=1 --loglevel=info
```

**Terminal 4 — Frontend Next.js**
```bash
cd aitools-frontend
npm install
npm run dev
```

**Optionnel — Dashboard Flower**
```bash
source .venv/bin/activate
celery -A core.celery_app flower --port=5555
```

---

## Créer le super-admin

Le super-admin a accès au dashboard d'administration (`GET /api/jobs/stats/platform`, `GET /api/jobs/all`).

```bash
# Avec Docker
docker compose exec api python scripts/create_superadmin.py

# Sans Docker (venv activé)
python scripts/create_superadmin.py
```

Le script est **idempotent** — relancez-le sans risque, il ne crée pas de doublon.

Le script demande l'email et le mot de passe au lancement (ou lit `SUPERADMIN_EMAIL` et `SUPERADMIN_PASSWORD`).
Choisissez un mot de passe d'au moins 12 caractères.

---

## Migrations Alembic

```bash
# Appliquer toutes les migrations en attente
alembic upgrade head

# Créer une nouvelle migration après modification d'un modèle
alembic revision --autogenerate -m "description du changement"
alembic upgrade head

# Revenir en arrière d'une migration
alembic downgrade -1

# Voir l'historique des migrations
alembic history

# Voir la migration courante
alembic current
```

---

## Endpoints disponibles

### Santé
| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/` | Info plateforme |
| GET | `/health` | Healthcheck |
| GET | `/docs` | Documentation Swagger interactive |
| GET | `/api/modules` | Liste tous les modules actifs |

### Auth
| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/api/auth/register` | Créer un compte |
| POST | `/api/auth/login` | Se connecter → token JWT |
| GET | `/api/auth/me` | Profil utilisateur (token requis) |

### Modules IA
| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/api/bg-remove/process` | Supprimer le fond d'une image |
| GET | `/api/bg-remove/result/{job_id}` | Télécharger le résultat |
| POST | `/api/transcribe/process` | Transcrire un fichier audio |
| GET | `/api/transcribe/result/{job_id}` | Télécharger la transcription |
| POST | `/api/ocr/process` | Extraire le texte d'une image |
| POST | `/api/pdf-merge/process` | Fusionner plusieurs PDFs |
| GET | `/api/pdf-merge/result/{job_id}` | Télécharger le PDF fusionné |
| POST | `/api/tts/process` | Convertir du texte en audio |
| GET | `/api/tts/result/{job_id}` | Télécharger l'audio MP3 |
| POST | `/api/compress-video/process` | Compresser une vidéo |
| GET | `/api/compress-video/result/{job_id}` | Télécharger la vidéo compressée |
| POST | `/api/summarize/process` | Résumer un texte |
| POST | `/api/convert-image/process` | Convertir une image |
| GET | `/api/convert-image/result/{job_id}` | Télécharger l'image convertie |

### Jobs & Stats
| Méthode | URL | Accès | Description |
|---------|-----|-------|-------------|
| GET | `/api/jobs/mine` | Connecté | Mes jobs (paginé) |
| GET | `/api/jobs/mine/{id}` | Connecté | Détail d'un job |
| GET | `/api/jobs/stats/modules` | Public | Stats par module |
| GET | `/api/jobs/stats/platform` | Admin | Dashboard global |
| GET | `/api/jobs/all` | Admin | Tous les jobs |

---

## Modules disponibles

| Module | Librairie | Entrée | Sortie |
|--------|-----------|--------|--------|
| Suppression de fond | rembg | Image | PNG transparent |
| Transcription audio | OpenAI Whisper | Audio | TXT / SRT / JSON |
| OCR | EasyOCR | Image | Texte brut |
| Fusion PDF | pypdf | 2–20 PDFs | PDF |
| Synthèse vocale | edge-tts | Texte (5 000 car.) | MP3 |
| Compression vidéo | ffmpeg | Vidéo | MP4 |
| Résumé de texte | sumy + nltk | Texte (50 000 car.) | Texte résumé |
| Conversion d'image | Pillow | Image | JPEG/PNG/WebP/BMP/TIFF |

---

## Ajouter un nouveau module

Créer le dossier `modules/mon_outil/` avec deux fichiers :

**`router.py`** — minimum requis :
```python
from fastapi import APIRouter
router = APIRouter()

MODULE_META = {
    "name": "Mon outil",
    "description": "Description courte",
    "version": "1.0.0",
    "prefix": "/mon-outil",
    "tags": ["mon-outil"],
}

@router.post("/process")
async def process():
    ...
```

**`service.py`** — logique métier / IA

C'est tout. **Redémarrer l'API** → le module est automatiquement détecté et enregistré.

---

## Variables d'environnement

Copier `.env.example` → `.env` et remplir :

```env
# Sécurité (OBLIGATOIRE en production)
SECRET_KEY=changez-moi-openssl-rand-hex-32

# Base de données PostgreSQL
DATABASE_URL=postgresql://aitools:aitools@localhost:5432/aitools

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Fichiers
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
MAX_FILE_SIZE_MB=50

# CORS (URLs du frontend autorisées)
ALLOWED_ORIGINS=["http://localhost:3000"]

# JWT
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ACCESS_TOKEN_REMEMBER_ME_DAYS=30
```

---

## Commandes utiles

```bash
# Voir les logs Docker en temps réel
docker compose logs -f api

# Redémarrer uniquement l'API
docker compose restart api

# Arrêter tous les services
docker compose down

# Arrêter et supprimer les volumes (reset complet BDD)
docker compose down -v

# Reconstruire sans cache
docker compose build --no-cache
```

---

## Licence

MIT — Open source, gratuit, pour toujours.
