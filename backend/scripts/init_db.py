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
from alembic.script import ScriptDirectory

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


def _get_current_revision() -> Optional[str]:
    """
    Récupère la révision actuelle de la base de données.
    
    Returns:
        str | None: ID de la révision courante ou None si aucune migration appliquée
    """
    try:
        from alembic.runtime.migration import MigrationContext
        from sqlalchemy import create_engine
        from database.connection import DATABASE_URL

        engine = create_engine(DATABASE_URL, poolclass=None)
        
        # Utilisation d'un context manager pour éviter les fuites de connexion
        with engine.connect() as connection:
            ctx = MigrationContext.configure(connection)
            current_rev = ctx.get_current_revision()
            return current_rev
    except Exception as e:
        print(f"⚠️  Erreur lors de la vérification de la révision : {e}")
        return None


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
        
        # Crée le dossier versions si nécessaire
        if not versions_dir.exists():
            print(f"   ➕ Création du dossier de versions : {versions_dir}")
            versions_dir.mkdir(parents=True, exist_ok=True)
            try:
                os.chmod(str(versions_dir), 0o775)
            except Exception:
                pass

        # Lister les fichiers de migration Python (exclure __pycache__)
        migration_files = [
            f for f in versions_dir.glob("*.py") 
            if f.name != "__init__.py" and not f.name.startswith(".")
        ]

        alembic_cfg = _alembic_config()

        if not migration_files:
            print("   ⚠️  Aucune migration détectée. Génération automatique...")
            try:
                os.chmod(str(versions_dir), 0o775)
            except Exception:
                pass

            command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
            print("✅ Migration initiale générée")
        else:
            print(f"   ✅ {len(migration_files)} migration(s) trouvée(s)")
            for mf in migration_files:
                print(f"      - {mf.name}")
                
    except Exception as e:
        print(f"❌ Erreur lors de la vérification/génération des migrations : {e}")
        traceback.print_exc()
        return False

    # 3) Vérifier la révision actuelle AVANT d'appliquer les migrations
    print("\n3️⃣  Vérification de l'état de la base de données...")
    current_rev = _get_current_revision()
    if current_rev:
        print(f"   📌 Révision actuelle : {current_rev}")
    else:
        print("   📌 Aucune révision appliquée (base vierge)")

    # 4) Appliquer les migrations
    print("\n4️⃣  Application des migrations...")
    try:
        alembic_cfg = _alembic_config()
        
        # Vérifier la révision HEAD (dernière migration disponible)
        script = ScriptDirectory.from_config(alembic_cfg)
        head_rev = script.get_current_head()
        
        if current_rev == head_rev:
            print(f"✅ Base de données déjà à jour (revision: {current_rev})")
        else:
            print(f"   🔄 Migration de {current_rev or 'base'} vers {head_rev}...")
            command.upgrade(alembic_cfg, "head")
            print("✅ Migrations appliquées avec succès")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution des migrations : {e}")
        traceback.print_exc()
        return False

    # 5) Vérification finale de la révision
    print("\n5️⃣  Vérification finale...")
    final_rev = _get_current_revision()
    if final_rev:
        print(f"✅ Base de données à jour (revision: {final_rev})")
    else:
        print("⚠️  Aucune migration appliquée")

    print("\n" + "=" * 60)
    print("✅ Initialisation terminée !")
    print("=" * 60 + "\n")
    return True


def reset_database() -> bool:
    """Reset complet (dev): downgrade to base then upgrade head."""
    print("🔄 RESET DATABASE - Suppression et recréation de toutes les tables")
    print("⚠️  Cette opération va SUPPRIMER toutes les données !")
    
    try:
        alembic_cfg = _alembic_config()
        
        print("\n1️⃣  Downgrade vers base (suppression des tables)...")
        command.downgrade(alembic_cfg, "base")
        print("✅ Tables supprimées")
        
        print("\n2️⃣  Upgrade vers head (recréation)...")
        command.upgrade(alembic_cfg, "head")
        print("✅ Tables recréées")
        
        print("\n✅ Reset effectué avec succès")
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