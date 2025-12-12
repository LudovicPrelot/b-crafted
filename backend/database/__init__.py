# backend/database/__init__.py
# Point d'entrée du package `database`.
# Module de gestion des connexions aux bases de données
# Ce fichier permet d'importer le module database comme un package Python
# Expose les fonctions utilitaires de `connection.py` au niveau du package

"""
Package `database`
===================

Ce module ré-exporte les fonctions et objets utiles de
`backend.database.connection` pour permettre des imports
directs comme `from database import check_db_connection`.

Tous les symboles exportés sont documentés dans `connection.py`.
"""

# Import relatif des utilitaires de connexion PostgreSQL
from .connection import (
	check_db_connection,
	get_db_info,
	get_db,
	init_db,
	SessionLocal,
	engine,
	Base,
)

# Liste des symboles exportés quand on fait `from database import *`
__all__ = [
	"check_db_connection",
	"get_db_info",
	"get_db",
	"init_db",
	"SessionLocal",
	"engine",
	"Base",
]