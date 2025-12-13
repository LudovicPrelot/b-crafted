# backend/utils/permissions.py
# Utilitaires de gestion des permissions utilisateur
# Vérifie les droits d'accès (admin, owner, etc.)

from fastapi import HTTPException, status
from models.user import UserResponse


def require_admin(current_user: UserResponse) -> None:
    """
    Vérifie que l'utilisateur actuel est administrateur.
    
    Args:
        current_user (UserResponse): Utilisateur authentifié
        
    Raises:
        HTTPException 403: Si l'utilisateur n'est pas admin
        
    Exemple d'utilisation dans une route:
        @router.delete("/users/{user_id}")
        def delete_user(
            user_id: int,
            current_user: UserResponse = Depends(get_current_user)
        ):
            require_admin(current_user)  # Vérifie les droits admin
            # ... suppression de l'utilisateur
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )


def require_owner_or_admin(current_user: UserResponse, target_user_id: int) -> None:
    """
    Vérifie que l'utilisateur actuel est soit le propriétaire, soit un admin.
    
    Args:
        current_user (UserResponse): Utilisateur authentifié
        target_user_id (int): ID de l'utilisateur cible
        
    Raises:
        HTTPException 403: Si l'utilisateur n'est ni le propriétaire ni admin
        
    Exemple d'utilisation:
        @router.put("/users/{user_id}")
        def update_user(
            user_id: int,
            current_user: UserResponse = Depends(get_current_user)
        ):
            require_owner_or_admin(current_user, user_id)
            # ... modification de l'utilisateur
    """
    is_owner = current_user.id == target_user_id
    is_admin = current_user.is_admin
    
    if not (is_owner or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own profile or be an admin"
        )


def is_owner(current_user: UserResponse, target_user_id: int) -> bool:
    """
    Vérifie si l'utilisateur actuel est le propriétaire.
    
    Args:
        current_user (UserResponse): Utilisateur authentifié
        target_user_id (int): ID de l'utilisateur cible
        
    Returns:
        bool: True si propriétaire, False sinon
    """
    return current_user.id == target_user_id


def is_admin(current_user: UserResponse) -> bool:
    """
    Vérifie si l'utilisateur actuel est administrateur.
    
    Args:
        current_user (UserResponse): Utilisateur authentifié
        
    Returns:
        bool: True si admin, False sinon
    """
    return current_user.is_admin


def check_resource_access(
    current_user: UserResponse,
    resource_owner_id: int,
    require_admin_only: bool = False
) -> bool:
    """
    Vérifie l'accès à une ressource (générique).
    
    Args:
        current_user (UserResponse): Utilisateur authentifié
        resource_owner_id (int): ID du propriétaire de la ressource
        require_admin_only (bool): Si True, seuls les admins ont accès
        
    Returns:
        bool: True si accès autorisé, False sinon
        
    Exemple:
        # Vérifier l'accès à un personnage
        if not check_resource_access(current_user, character.user_id):
            raise HTTPException(403, "Access denied")
    """
    if require_admin_only:
        return current_user.is_admin
    
    return current_user.is_admin or current_user.id == resource_owner_id