"""
Alembic env.py — configuration async pour PostgreSQL + asyncpg.

Usage :
    alembic revision --autogenerate -m "description"
    alembic upgrade head
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# ── Import de la config et des modèles ────────────────────────────────────────
# IMPORTANT : tous les modèles doivent être importés ici pour que
# l'autogenerate détecte les tables à créer/modifier.

from core.config import settings
from core.database import Base

# Import de TOUS les modèles (même si non utilisés directement ici)
from modules.auth.models import User        # noqa: F401
from modules.jobs.models import Job, ModuleStat  # noqa: F401

# ── Config Alembic ────────────────────────────────────────────────────────────

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Surcharge l'URL avec celle de settings (évite de dupliquer des secrets)
db_url = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://", 1
)
config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata


# ── Mode offline (génère le SQL sans connexion) ───────────────────────────────

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Mode online (async) ──────────────────────────────────────────────────────

def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# ── Point d'entrée ────────────────────────────────────────────────────────────

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
