# backend/models/__init__.py
# Module des modèles Pydantic pour la validation des données
# Ce fichier permet d'importer le module models comme un package Python

"""
Module models
=============

Contient les modèles Pydantic pour la validation des données API.

Les modèles Pydantic servent à :
- Valider les données entrantes (requêtes API)
- Valider les données sortantes (réponses API)
- Générer automatiquement la documentation OpenAPI/Swagger
- Assurer la cohérence des types de données

Contenu actuel :
- user.py : Modèles User (UserCreate, UserUpdate, UserResponse, UserLogin, Token)
- pagination.py : Modèles de pagination (PaginatedResponse, PaginationMetadata)

Contenu futur :
- character.py : Modèles Character
- profession.py : Modèles Profession
- resource.py : Modèles Resource
- recipe.py : Modèles Recipe
"""

# Import des modèles User
from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    Token
)

# Import des modèles de pagination
from .pagination import (
    PaginationMetadata,
    PaginatedResponse,
    create_paginated_response
)

# Liste des objets exportés par le module
__all__ = [
    # User models
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "Token",
    # Pagination models
    "PaginationMetadata",
    "PaginatedResponse",
    "create_paginated_response"
]