# backend/routes/users.py
# Routes CRUD pour la gestion des utilisateurs
# Endpoints REST avec authentification et permissions

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Annotated, Optional

from database import get_db
from models.user import UserResponse, UserUpdate
from models.pagination import PaginatedResponse, create_paginated_response
from services import user_service
from routes.auth import get_current_user, get_current_active_user
from utils.permissions import require_admin, require_owner_or_admin

# ============================================
# CONFIGURATION DU ROUTER
# ============================================
router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={
        401: {"description": "Unauthorized - Authentication required"},
        403: {"description": "Forbidden - Insufficient permissions"},
        404: {"description": "Not Found - User not found"}
    }
)


# ============================================
# ROUTES PUBLIQUES (sans auth)
# ============================================
@router.get(
    "/count",
    response_model=dict,
    summary="Get total number of users",
    description="Returns the total count of active users (public endpoint)"
)
async def count_users(
    db: Session = Depends(get_db),
    is_active: Optional[bool] = Query(True, description="Filter by active status")
) -> dict:
    """
    Compte le nombre total d'utilisateurs.
    Endpoint public pour statistiques.
    
    Args:
        db (Session): Session de base de données
        is_active (bool, optional): Filtrer par statut actif/inactif
        
    Returns:
        dict: Nombre total d'utilisateurs
        
    Exemple de requête:
        GET /users/count
        GET /users/count?is_active=true
    """
    total = user_service.count_users(db, is_active=is_active)
    return {
        "total": total,
        "is_active": is_active
    }


# ============================================
# ROUTES PROTÉGÉES (avec auth)
# ============================================
@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    summary="Get paginated list of users",
    description="Returns a paginated list of users (admin only)"
)
async def list_users(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    is_active: Optional[bool] = Query(None, description="Filter by active status")
) -> PaginatedResponse[UserResponse]:
    """
    Liste paginée des utilisateurs.
    Accessible uniquement aux administrateurs.
    
    Args:
        db (Session): Session de base de données
        current_user (UserResponse): Utilisateur authentifié
        page (int): Numéro de la page (commence à 1)
        per_page (int): Nombre d'éléments par page (max 100)
        is_active (bool, optional): Filtrer par statut actif/inactif
        
    Returns:
        PaginatedResponse[UserResponse]: Liste paginée d'utilisateurs
        
    Raises:
        HTTPException 403: Si l'utilisateur n'est pas admin
        
    Exemple de requête:
        GET /users?page=1&per_page=10
        GET /users?page=2&per_page=20&is_active=true
        
        Headers:
            Authorization: Bearer <token_jwt>
    """
    # Vérification des droits admin
    require_admin(current_user)
    
    # Calcul du skip pour la pagination
    skip = (page - 1) * per_page
    
    # Récupération des utilisateurs
    users = user_service.get_users(db, skip=skip, limit=per_page, is_active=is_active)
    
    # Compte total
    total = user_service.count_users(db, is_active=is_active)
    
    # Conversion en modèles Pydantic
    users_response = [UserResponse.model_validate(user) for user in users]
    
    # Création de la réponse paginée
    return create_paginated_response(
        items=users_response,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Returns the profile of the currently authenticated user"
)
async def get_my_profile(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
) -> UserResponse:
    """
    Récupère le profil de l'utilisateur actuel.
    Alternative à /auth/me (pour cohérence avec /users).
    
    Args:
        current_user (UserResponse): Utilisateur authentifié
        
    Returns:
        UserResponse: Profil de l'utilisateur
        
    Exemple de requête:
        GET /users/me
        Headers:
            Authorization: Bearer <token_jwt>
    """
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Returns details of a specific user (admin or owner only)"
)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
) -> UserResponse:
    """
    Récupère un utilisateur par son ID.
    Accessible aux admins ou au propriétaire du compte.
    
    Args:
        user_id (int): ID de l'utilisateur
        db (Session): Session de base de données
        current_user (UserResponse): Utilisateur authentifié
        
    Returns:
        UserResponse: Détails de l'utilisateur
        
    Raises:
        HTTPException 403: Si l'utilisateur n'a pas les permissions
        HTTPException 404: Si l'utilisateur n'existe pas
        
    Exemple de requête:
        GET /users/1
        Headers:
            Authorization: Bearer <token_jwt>
    """
    # Vérification des permissions (admin ou propriétaire)
    require_owner_or_admin(current_user, user_id)
    
    # Récupération de l'utilisateur
    db_user = user_service.get_user_by_id(db, user_id)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return UserResponse.model_validate(db_user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Updates user information (owner or admin only)"
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
) -> UserResponse:
    """
    Met à jour les informations d'un utilisateur.
    Accessible au propriétaire ou aux admins.
    
    Args:
        user_id (int): ID de l'utilisateur à modifier
        user_data (UserUpdate): Données à mettre à jour
        db (Session): Session de base de données
        current_user (UserResponse): Utilisateur authentifié
        
    Returns:
        UserResponse: Utilisateur mis à jour
        
    Raises:
        HTTPException 403: Si l'utilisateur n'a pas les permissions
        HTTPException 404: Si l'utilisateur n'existe pas
        HTTPException 409: Si l'email/username existe déjà
        
    Exemple de requête:
        PUT /users/1
        Headers:
            Authorization: Bearer <token_jwt>
        Body:
        {
            "first_name": "John",
            "last_name": "Smith"
        }
    """
    # Vérification des permissions (admin ou propriétaire)
    require_owner_or_admin(current_user, user_id)
    
    # Vérification que l'utilisateur existe
    db_user = user_service.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Règle métier : Un utilisateur non-admin ne peut pas se promouvoir admin
    if not current_user.is_admin and user_data.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot deactivate your own account"
        )
    
    # Mise à jour de l'utilisateur
    try:
        updated_user = user_service.update_user(db, user_id, user_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        return UserResponse.model_validate(updated_user)
        
    except ValueError as e:
        # Email ou username déjà existant
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Soft deletes a user (admin only, deactivates account)"
)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user),
    hard_delete: bool = Query(False, description="If true, permanently delete (dangerous!)")
) -> None:
    """
    Supprime un utilisateur (soft delete par défaut).
    Accessible uniquement aux administrateurs.
    
    Args:
        user_id (int): ID de l'utilisateur à supprimer
        db (Session): Session de base de données
        current_user (UserResponse): Utilisateur authentifié
        hard_delete (bool): Si True, suppression définitive (déconseillé)
        
    Raises:
        HTTPException 403: Si l'utilisateur n'est pas admin
        HTTPException 404: Si l'utilisateur n'existe pas
        HTTPException 400: Si tentative de suppression de son propre compte
        
    Exemple de requête:
        DELETE /users/1
        DELETE /users/1?hard_delete=true  # Suppression définitive
        
        Headers:
            Authorization: Bearer <token_jwt>
    """
    # Vérification des droits admin
    require_admin(current_user)
    
    # Règle métier : Un admin ne peut pas supprimer son propre compte
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account"
        )
    
    # Suppression de l'utilisateur
    success = user_service.delete_user(db, user_id, soft_delete=not hard_delete)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # 204 No Content (pas de body dans la réponse)
    return None


@router.post(
    "/{user_id}/activate",
    response_model=UserResponse,
    summary="Activate user account",
    description="Reactivates a deactivated user account (admin only)"
)
async def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
) -> UserResponse:
    """
    Réactive un compte utilisateur désactivé.
    Accessible uniquement aux administrateurs.
    
    Args:
        user_id (int): ID de l'utilisateur à activer
        db (Session): Session de base de données
        current_user (UserResponse): Utilisateur authentifié
        
    Returns:
        UserResponse: Utilisateur réactivé
        
    Raises:
        HTTPException 403: Si l'utilisateur n'est pas admin
        HTTPException 404: Si l'utilisateur n'existe pas
        
    Exemple de requête:
        POST /users/1/activate
        Headers:
            Authorization: Bearer <token_jwt>
    """
    # Vérification des droits admin
    require_admin(current_user)
    
    # Activation de l'utilisateur
    success = user_service.activate_user(db, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Récupération de l'utilisateur activé
    db_user = user_service.get_user_by_id(db, user_id)
    return UserResponse.model_validate(db_user)


@router.post(
    "/{user_id}/deactivate",
    response_model=UserResponse,
    summary="Deactivate user account",
    description="Deactivates a user account (admin only)"
)
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
) -> UserResponse:
    """
    Désactive un compte utilisateur.
    Accessible uniquement aux administrateurs.
    
    Args:
        user_id (int): ID de l'utilisateur à désactiver
        db (Session): Session de base de données
        current_user (UserResponse): Utilisateur authentifié
        
    Returns:
        UserResponse: Utilisateur désactivé
        
    Raises:
        HTTPException 403: Si l'utilisateur n'est pas admin
        HTTPException 404: Si l'utilisateur n'existe pas
        HTTPException 400: Si tentative de désactivation de son propre compte
        
    Exemple de requête:
        POST /users/1/deactivate
        Headers:
            Authorization: Bearer <token_jwt>
    """
    # Vérification des droits admin
    require_admin(current_user)
    
    # Règle métier : Un admin ne peut pas désactiver son propre compte
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account"
        )
    
    # Désactivation de l'utilisateur
    success = user_service.deactivate_user(db, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Récupération de l'utilisateur désactivé
    db_user = user_service.get_user_by_id(db, user_id)
    return UserResponse.model_validate(db_user)