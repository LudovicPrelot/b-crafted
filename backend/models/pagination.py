# backend/models/pagination.py
# Modèles Pydantic pour la pagination des résultats
# Permet de retourner des listes paginées avec métadonnées

from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional

# Type générique pour permettre PaginatedResponse[UserResponse], etc.
T = TypeVar('T')


class PaginationMetadata(BaseModel):
    """
    Métadonnées de pagination.
    Contient les informations sur la page actuelle et le nombre total d'éléments.
    """
    total: int = Field(
        ...,
        description="Nombre total d'éléments disponibles",
        examples=[150]
    )
    page: int = Field(
        ...,
        ge=1,
        description="Numéro de la page actuelle (commence à 1)",
        examples=[1]
    )
    per_page: int = Field(
        ...,
        ge=1,
        le=100,
        description="Nombre d'éléments par page",
        examples=[10]
    )
    total_pages: int = Field(
        ...,
        description="Nombre total de pages",
        examples=[15]
    )
    has_next: bool = Field(
        ...,
        description="Indique s'il existe une page suivante",
        examples=[True]
    )
    has_prev: bool = Field(
        ...,
        description="Indique s'il existe une page précédente",
        examples=[False]
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Réponse paginée générique.
    Peut être utilisée pour n'importe quel type de données (User, Character, etc.)
    
    Exemple d'utilisation:
        PaginatedResponse[UserResponse]  # Pour une liste d'utilisateurs
        PaginatedResponse[CharacterResponse]  # Pour une liste de personnages
    """
    items: List[T] = Field(
        ...,
        description="Liste des éléments de la page actuelle"
    )
    metadata: PaginationMetadata = Field(
        ...,
        description="Métadonnées de pagination"
    )
    
    class Config:
        # Permet d'utiliser des types génériques
        arbitrary_types_allowed = True


def create_paginated_response(
    items: List[T],
    total: int,
    page: int,
    per_page: int
) -> PaginatedResponse[T]:
    """
    Fonction utilitaire pour créer une réponse paginée.
    
    Args:
        items (List[T]): Liste des éléments de la page actuelle
        total (int): Nombre total d'éléments disponibles
        page (int): Numéro de la page actuelle (commence à 1)
        per_page (int): Nombre d'éléments par page
        
    Returns:
        PaginatedResponse[T]: Réponse paginée avec métadonnées
        
    Exemple:
        users = get_users(db, skip=0, limit=10)
        total = count_users(db)
        paginated = create_paginated_response(
            items=users,
            total=total,
            page=1,
            per_page=10
        )
    """
    # Calcul du nombre total de pages
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    # Métadonnées
    metadata = PaginationMetadata(
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )
    
    return PaginatedResponse(
        items=items,
        metadata=metadata
    )