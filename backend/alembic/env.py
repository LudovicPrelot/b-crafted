# backend/alembic/env.py
# Configuration de l'environnement Alembic
# Ce fichier est exécuté par Alembic pour se connecter à la base de données

from logging.config import fileConfig
import os
from sqlalchemy import create_engine, pool
from alembic import context

# Importation de la Base et de tous les schémas SQLAlchemy
# IMPORTANT: importer tous les modèles pour qu'Alembic les détecte
from database.connection import DATABASE_URL

# Import de tous les schémas (pour autogenerate)
try:
    from schemas.base import Base
    # Import explicite de tous les modèles pour qu'Alembic les détecte
    from schemas.user import User
except ImportError as e:
    # Fallback si les chemins diffèrent
    print(f"⚠️ Erreur d'import : {e}")
    try:
        from backend.schemas.base import Base
        from backend.schemas.user import User
    except ImportError:
        print("❌ Impossible d'importer les schémas")
        raise

# ============================================
# CONFIGURATION ALEMBIC
# ============================================
# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Surcharge de l'URL de connexion avec les variables d'environnement
# Utilise DATABASE_URL depuis database/connection.py
if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


# ============================================
# FONCTIONS ALEMBIC
# ============================================
def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode using DATABASE_URL.
    
    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode using an Engine created from DATABASE_URL.
    
    In this scenario we need to create an Engine and associate a connection with the context.
    """
    # Utilisation de NullPool pour éviter les problèmes de connexions
    # lors des migrations (pas de pooling = pas de connexions persistantes)
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,  # ← Important pour éviter les locks
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_schemas=False,
            # render_as_batch=True,  # Optionnel : pour SQLite
        )

        with context.begin_transaction():
            context.run_migrations()


# ============================================
# POINT D'ENTRÉE
# ============================================
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()