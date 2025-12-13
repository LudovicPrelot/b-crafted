# backend/scripts/init_db.py
# Script d'initialisation de la base de données
# Exécute les migrations Alembic et crée les tables si nécessaire
# Peut être utilisé de manière standalone ou appelé depuis main.py

import os
import sys
import traceback
from pathlib import Path
from typing import Optional

from alembic.config import Config
from alembic import command

from database.connection import check_db_connection, get_db_info

# Répertoires
BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
ALEMBIC_DIR = BASE_DIR / "alembic"
CONFIG_DIR = BASE_DIR / "config"


def _alembic_config() -> Config:
    """Renvoie une instance Config pour Alembic utilisant le fichier de config absolu."""
    cfg_path = CONFIG_DIR / "alembic.ini"
    cfg = Config(str(cfg_path))
    # S'assurer que l'URL utilisée par Alembic vient des variables d'environnement
    # Si DATABASE_URL est fournie via database/connection, on la laisse (optionnel)
    return cfg


def init_database() -> bool:
    """
    Initialise la base de données en exécutant (ou en créant) les migrations Alembic.

    Retourne True si tout s'est bien passé, False sinon.
    """
    print("=" * 60)
    print("🚀 B'Craft'D - Initialisation de la base de données")
    print("=" * 60)

    # 1) Vérifier la connexion PostgreSQL
    print("\n1️⃣  Vérification de la connexion PostgreSQL...")
    if not check_db_connection():
        print("❌ Erreur : Impossible de se connecter à PostgreSQL")
        print("💡 Vérifiez que le container PostgreSQL est démarré et les vars d'environnement")
        return False

    print("✅ Connexion PostgreSQL établie")
    db_info = get_db_info()
    print(f"   📍 Host     : {db_info['host']}")
    print(f"   📍 Port     : {db_info['port']}")
    print(f"   📍 Database : {db_info['database']}")
    print(f"   📍 User     : {db_info['user']}")

    # 2) Vérifier si des migrations existent; si non, générer une initiale
    print("\n2️⃣  Vérification des migrations...")
    try:
        versions_dir = ALEMBIC_DIR / "versions"
        # Crée le dossier versions si nécessaire et s'assure des droits en écriture
        if not versions_dir.exists():
            print(f"   ➕ Création du dossier de versions : {versions_dir}")
            versions_dir.mkdir(parents=True, exist_ok=True)
            try:
                # Tentative de définir des permissions larges (rwxrwxr-x)
                os.chmod(str(versions_dir), 0o775)
            except Exception:
                # Si chmod échoue (ex : système de fichiers Windows), on ignore
                pass

        migration_files = list(versions_dir.glob("*.py"))

        alembic_cfg = _alembic_config()

        if not migration_files:
            print("   ⚠️  Aucune migration détectée. Génération automatique...")
            # Générer une migration initiale
            # Alembic a besoin que le template (script.py.mako) existe dans alembic/
            # On s'assure encore une fois que le dossier a les droits avant d'écrire
            try:
                os.chmod(str(versions_dir), 0o775)
            except Exception:
                pass

            command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
            print("✅ Migration initiale générée")
        else:
            print(f"   ✅ {len(migration_files)} migration(s) trouvée(s)")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification/génération des migrations : {e}")
        traceback.print_exc()
        return False

    # 3) Appliquer les migrations
    print("\n3️⃣  Application des migrations...")
    try:
        # Recharger la config pour être sûr
        alembic_cfg = _alembic_config()
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations appliquées avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution des migrations : {e}")
        traceback.print_exc()
        return False

    # 4) Vérification finale de la révision
    print("\n4️⃣  Vérification finale...")
    try:
        from alembic.runtime.migration import MigrationContext
        from sqlalchemy import create_engine
        from database.connection import DATABASE_URL

        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            ctx = MigrationContext.configure(connection)
            current_rev = ctx.get_current_revision()
            if current_rev:
                print(f"✅ Base de données à jour (revision: {current_rev})")
            else:
                print("⚠️  Aucune migration appliquée")
    except Exception as e:
        print(f"⚠️  Impossible de vérifier la version : {e}")
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ Initialisation terminée !")
    print("=" * 60 + "\n")
    return True


def reset_database() -> bool:
    """Reset complet (dev): downgrade to base then upgrade head."""
    try:
        alembic_cfg = _alembic_config()
        print("🔄 Downgrade vers base (suppression des tables)...")
        command.downgrade(alembic_cfg, "base")
        print("🔄 Upgrade vers head (recréation)...")
        command.upgrade(alembic_cfg, "head")
        print("✅ Reset effectué")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du reset : {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Exécution standalone
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        ok = reset_database()
    else:
        ok = init_database()
    sys.exit(0 if ok else 1)
