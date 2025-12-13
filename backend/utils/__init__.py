# backend/utils/__init__.py
# Module des utilitaires partagés
# Ce fichier permet d'importer le module utils comme un package Python

"""
Module utils
============

Contient les utilitaires et helpers partagés de l'application.

Les utilitaires sont des fonctions réutilisables :
- Sécurité (hachage, JWT)
- Formatage de données
- Validations communes
- Helpers divers

Contenu actuel :
- security.py : Utilitaires de sécurité (bcrypt, JWT)

Contenu futur :
- formatters.py : Formatage de données
- validators.py : Validations personnalisées
- helpers.py : Fonctions helpers diverses
"""

# Import des fonctions de sécurité
from .security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    verify_token,
    get_token_expiration_time,
    is_token_expired
)

# Liste des objets exportés par le module
__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "verify_token",
    "get_token_expiration_time",
    "is_token_expired"
]