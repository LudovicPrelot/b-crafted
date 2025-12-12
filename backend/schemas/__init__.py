# backend/schemas/__init__.py
# Module des schémas SQLAlchemy pour l'ORM
# Ce fichier permet d'importer le module schemas comme un package Python

"""
Module schemas
==============

Contient les schémas SQLAlchemy (ORM) pour la base de données PostgreSQL.

Les schémas SQLAlchemy servent à :
- Définir la structure des tables SQL
- Gérer les relations entre tables (Foreign Keys)
- Mapper les objets Python aux lignes de la base de données
- Faciliter les requêtes SQL via l'ORM

Différence entre models/ et schemas/ :
- models/ : Pydantic (validation API, JSON)
- schemas/ : SQLAlchemy (structure DB, SQL)

Contenu futur :
- base.py : Configuration de base SQLAlchemy (DeclarativeBase)
- user.py : Table users
- character.py : Table characters
- profession.py : Table professions
- resource.py : Table resources
- recipe.py : Table recipes
"""

# Import de la base et des mixins
from .base import Base, TimestampMixin

# Import du schéma User
from .user import User

# Liste des objets exportés par le module
__all__ = [
    "Base",
    "TimestampMixin",
    "User"
]