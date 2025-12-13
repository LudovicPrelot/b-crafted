# backend/services/user_service.py
# Service métier pour la gestion des utilisateurs
# Contient la logique métier (DDD) séparée des routes (API)

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text, or_
from schemas.user import User
from models.user import UserCreate, UserUpdate, UserResponse
from utils.security import hash_password, verify_password


# ============================================
# FONCTIONS DE CRÉATION
# ============================================
def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Crée un nouvel utilisateur dans la base de données.
    
    Args:
        db (Session): Session SQLAlchemy
        user_data (UserCreate): Données validées de l'utilisateur
        
    Returns:
        User: Utilisateur créé
        
    Raises:
        ValueError: Si l'email ou le username existe déjà
        
    Exemple:
        new_user = create_user(db, UserCreate(
            email="john@example.com",
            username="JohnDoe",
            first_name="John",
            last_name="Doe",
            password="MyS3cur3P@ssw0rd"
        ))
    """
    # Vérification de l'existence de l'email
    if get_user_by_email(db, user_data.email):
        raise ValueError(f"Email '{user_data.email}' already exists")
    
    # Vérification de l'existence du username
    if get_user_by_username(db, user_data.username):
        raise ValueError(f"Username '{user_data.username}' already exists")
    
    # Hachage du mot de passe
    hashed_password = hash_password(user_data.password)
    
    # Création de l'objet User SQLAlchemy
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        password=hashed_password,
        is_active=True,
        is_admin=False
    )
    
    # Ajout en base de données
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


# ============================================
# FONCTIONS DE LECTURE
# ============================================
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Récupère un utilisateur par son ID.
    
    Args:
        db (Session): Session SQLAlchemy
        user_id (int): ID de l'utilisateur
        
    Returns:
        User | None: Utilisateur trouvé ou None
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_uuid(db: Session, user_uuid: str) -> Optional[User]:
    """
    Récupère un utilisateur par son UUID.
    
    Args:
        db (Session): Session SQLAlchemy
        user_uuid (str): UUID de l'utilisateur
        
    Returns:
        User | None: Utilisateur trouvé ou None
    """
    return db.query(User).filter(User.uuid == user_uuid).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Récupère un utilisateur par son email.
    
    Args:
        db (Session): Session SQLAlchemy
        email (str): Email de l'utilisateur
        
    Returns:
        User | None: Utilisateur trouvé ou None
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Récupère un utilisateur par son username.
    
    Args:
        db (Session): Session SQLAlchemy
        username (str): Username de l'utilisateur
        
    Returns:
        User | None: Utilisateur trouvé ou None
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_identifier(db: Session, identifier: str) -> Optional[User]:
    """
    Récupère un utilisateur par email OU username.
    Utile pour le login où l'utilisateur peut saisir l'un ou l'autre.
    
    Args:
        db (Session): Session SQLAlchemy
        identifier (str): Email ou username
        
    Returns:
        User | None: Utilisateur trouvé ou None
        
    Exemple:
        user = get_user_by_identifier(db, "john@example.com")
        user = get_user_by_identifier(db, "JohnDoe")
    """
    return db.query(User).filter(
        or_(User.email == identifier, User.username == identifier)
    ).first()


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[User]:
    """
    Récupère une liste d'utilisateurs avec pagination.
    
    Args:
        db (Session): Session SQLAlchemy
        skip (int): Nombre d'enregistrements à sauter (pagination)
        limit (int): Nombre maximum d'enregistrements à retourner
        is_active (bool, optional): Filtrer par statut actif/inactif
        
    Returns:
        List[User]: Liste des utilisateurs
        
    Exemple:
        # Récupérer les 10 premiers utilisateurs actifs
        users = get_users(db, skip=0, limit=10, is_active=True)
    """
    query = db.query(User)
    
    # Filtre optionnel sur is_active
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


def count_users(db: Session, is_active: Optional[bool] = None) -> int:
    """
    Compte le nombre total d'utilisateurs.
    
    Args:
        db (Session): Session SQLAlchemy
        is_active (bool, optional): Filtrer par statut actif/inactif
        
    Returns:
        int: Nombre d'utilisateurs
    """
    query = db.query(User)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    return query.count()


# ============================================
# FONCTIONS DE MISE À JOUR
# ============================================
def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
    """
    Met à jour un utilisateur existant.
    
    Args:
        db (Session): Session SQLAlchemy
        user_id (int): ID de l'utilisateur à modifier
        user_data (UserUpdate): Données à mettre à jour (champs optionnels)
        
    Returns:
        User | None: Utilisateur mis à jour ou None si non trouvé
        
    Raises:
        ValueError: Si l'email/username existe déjà pour un autre utilisateur
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    # Mise à jour des champs fournis
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Vérification de l'unicité de l'email (si modifié)
    if "email" in update_data and update_data["email"] != db_user.email:
        existing = get_user_by_email(db, update_data["email"])
        if existing and existing.id != user_id:
            raise ValueError(f"Email '{update_data['email']}' already exists")
    
    # Vérification de l'unicité du username (si modifié)
    if "username" in update_data and update_data["username"] != db_user.username:
        existing = get_user_by_username(db, update_data["username"])
        if existing and existing.id != user_id:
            raise ValueError(f"Username '{update_data['username']}' already exists")
    
    # Hachage du nouveau mot de passe (si fourni)
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])
    
    # Application des modifications
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


# ============================================
# FONCTIONS DE SUPPRESSION
# ============================================
def delete_user(db: Session, user_id: int, soft_delete: bool = True) -> bool:
    """
    Supprime un utilisateur (soft delete par défaut).
    
    Args:
        db (Session): Session SQLAlchemy
        user_id (int): ID de l'utilisateur à supprimer
        soft_delete (bool): Si True, désactive le compte au lieu de supprimer
        
    Returns:
        bool: True si suppression réussie, False sinon
        
    Note:
        - Soft delete (défaut) : is_active = False
        - Hard delete : Suppression physique de la ligne (déconseillé)
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    if soft_delete:
        # Soft delete : désactivation du compte
        db_user.is_active = False
        db.commit()
    else:
        # Hard delete : suppression physique (déconseillé)
        db.delete(db_user)
        db.commit()
    
    return True


# ============================================
# FONCTIONS D'AUTHENTIFICATION
# ============================================
def authenticate_user(db: Session, identifier: str, password: str) -> Optional[User]:
    """
    Authentifie un utilisateur avec email/username + mot de passe.
    
    Args:
        db (Session): Session SQLAlchemy
        identifier (str): Email ou username
        password (str): Mot de passe en clair
        
    Returns:
        User | None: Utilisateur authentifié ou None si échec
        
    Exemple:
        user = authenticate_user(db, "john@example.com", "MyS3cur3P@ssw0rd")
        if user:
            # Authentification réussie
            token = create_access_token({"sub": user.email})
        else:
            # Credentials invalides
    """
    # Récupération de l'utilisateur
    user = get_user_by_identifier(db, identifier)
    
    if not user:
        return None
    
    # Vérification du mot de passe
    if not verify_password(password, user.password):
        return None
    
    # Vérification que le compte est actif
    if not user.is_active:
        return None
    
    return user


def activate_user(db: Session, user_id: int) -> bool:
    """
    Active un compte utilisateur désactivé.
    
    Args:
        db (Session): Session SQLAlchemy
        user_id (int): ID de l'utilisateur
        
    Returns:
        bool: True si activation réussie, False sinon
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    db_user.is_active = True
    db.commit()
    
    return True


def deactivate_user(db: Session, user_id: int) -> bool:
    """
    Désactive un compte utilisateur.
    
    Args:
        db (Session): Session SQLAlchemy
        user_id (int): ID de l'utilisateur
        
    Returns:
        bool: True si désactivation réussie, False sinon
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    db_user.is_active = False
    db.commit()
    
    return True