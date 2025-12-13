# backend/services/__init__.py
# Module des services métier (logique applicative)
# Ce fichier permet d'importer le module services comme un package Python

"""
Module services
===============

Contient les services métier (business logic) de l'application.

Les services encapsulent la logique métier (DDD) :
- Opérations CRUD complexes
- Règles métier
- Validations métier
- Orchestration de plusieurs opérations
- Gestion des transactions

Différence entre routes/ et services/ :
- routes/ : Gestion HTTP, validation requêtes, formatage réponses
- services/ : Logique métier pure, indépendante de HTTP

Contenu actuel :
- user_service.py : Logique métier utilisateurs

Contenu futur :
- character_service.py : Logique métier personnages
- profession_service.py : Logique métier professions
- resource_service.py : Logique métier ressources
- recipe_service.py : Logique métier recettes
"""

# Import du service utilisateur
from . import user_service

# Liste des objets exportés par le module
__all__ = [
    "user_service"
]