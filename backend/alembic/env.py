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
try:
	from schemas.base import Base
except Exception:
	# Fallback si les chemins diffèrent
	from backend.schemas.base import Base

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
	"""Run migrations in 'offline' mode using DATABASE_URL."""
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
	"""Run migrations in 'online' mode using an Engine created from DATABASE_URL."""
	connectable = create_engine(
		DATABASE_URL,
		poolclass=pool.NullPool,
	)

	with connectable.connect() as connection:
		context.configure(
			connection=connection,
			target_metadata=target_metadata,
			compare_type=True,
			compare_server_default=True,
			include_schemas=False,
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

