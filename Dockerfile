# ─── Build stage ──────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Dépendances système (ffmpeg pour Whisper, libgl pour OpenCV/rembg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python de base
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip "setuptools<70" wheel

# Optimisation : Installer PyTorch CPU en priorité (gain de ~1.5 Go et build + rapide)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Installer Whisper sans isolation de build (pour pkg_resources)
RUN pip install --no-cache-dir openai-whisper==20231117 --no-build-isolation

# Installer le reste des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# ─── Runtime stage ────────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Dépendances runtime uniquement
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copier les packages Python installés
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copier le code source
COPY . .

# Créer les dossiers de stockage
RUN mkdir -p uploads outputs

# Utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Port exposé
EXPOSE 8000

# Lancement
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
