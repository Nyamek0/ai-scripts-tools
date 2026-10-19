"""
Script de création du super-administrateur AITools Platform.

Usage:
    SUPERADMIN_EMAIL=vous@example.com python scripts/create_superadmin.py
    (le mot de passe est demandé au clavier, ou lu depuis SUPERADMIN_PASSWORD)

À exécuter une seule fois après le premier démarrage de la base de données.
Idempotent : ne fait rien si le compte existe déjà.
"""
import asyncio
import getpass
import os
import sys

# Ajoute la racine du projet au path pour les imports (core.*, modules.*)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import create_all_tables, AsyncSessionLocal
from core.security import hash_password
from modules.auth.models import User
from modules.auth.service import get_user_by_email

MIN_PASSWORD_LENGTH = 12


def read_credentials() -> tuple[str, str, str]:
    """Lit l'email, le nom et le mot de passe sans jamais les stocker dans le code."""
    email = os.getenv("SUPERADMIN_EMAIL") or input("Email du super-admin : ").strip()
    name = os.getenv("SUPERADMIN_NAME", "Super Admin")
    password = os.getenv("SUPERADMIN_PASSWORD") or getpass.getpass("Mot de passe : ")

    if not email:
        sys.exit("❌ Email requis.")
    if len(password) < MIN_PASSWORD_LENGTH:
        sys.exit(f"❌ Mot de passe trop court (minimum {MIN_PASSWORD_LENGTH} caractères).")
    return email, name, password


async def main() -> None:
    print("🔧 AITools Platform — Création du super-administrateur")
    print("-" * 55)

    email, name, password = read_credentials()

    # S'assure que les tables existent
    await create_all_tables()

    async with AsyncSessionLocal() as db:
        existing = await get_user_by_email(db, email)

        if existing:
            if existing.is_superadmin:
                print(f"✅ Le super-admin existe déjà : {email}")
            else:
                # Compte existant mais pas superadmin → promouvoir
                existing.is_superadmin = True
                existing.is_verified = True
                await db.commit()
                print(f"🔼 Compte promu super-admin : {email}")
            return

        superadmin = User(
            email=email.lower(),
            hashed_password=hash_password(password),
            full_name=name,
            is_active=True,
            is_verified=True,
            is_superadmin=True,
        )
        db.add(superadmin)
        await db.commit()
        await db.refresh(superadmin)

        print("✅ Super-admin créé avec succès !")
        print(f"   Email    : {superadmin.email}")
        print(f"   Nom      : {superadmin.full_name}")
        print(f"   ID       : {superadmin.id}")
        print(f"   Créé le  : {superadmin.created_at}")


if __name__ == "__main__":
    asyncio.run(main())
