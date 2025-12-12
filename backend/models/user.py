# backend/models/user.py
# Modèles Pydantic pour l'entité User (Utilisateur)
# Gère la validation des données pour l'authentification et la gestion des utilisateurs

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime


# ============================================
# MODÈLE DE BASE USER
# ============================================
class UserBase(BaseModel):
    """
    Modèle de base User contenant les champs communs.
    Ne contient ni l'ID ni le mot de passe.
    """
    email: EmailStr = Field(
        ...,
        description="Adresse email de l'utilisateur (unique)",
        examples=["john.doe@example.com"]
    )
    pseudo: str = Field(
        ...,
        min_length=3,
        max_length=20,
        description="Pseudo de l'utilisateur (unique, entre 3 et 20 caractères)",
        examples=["JohnDoe"]
    )
    nom: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Nom de famille de l'utilisateur",
        examples=["Doe"]
    )
    prenom: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Prénom de l'utilisateur",
        examples=["John"]
    )
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('pseudo')
    @classmethod
    def validate_pseudo(cls, v: str) -> str:
        """
        Valide que le pseudo ne contient que des caractères alphanumériques et underscores.
        """
        if not v.replace('_', '').isalnum():
            raise ValueError('Le pseudo ne peut contenir que des lettres, chiffres et underscores')
        return v


# ============================================
# MODÈLE CREATE - Inscription
# ============================================
class UserCreate(UserBase):
    """
    Modèle pour la création d'un utilisateur (inscription).
    Contient le mot de passe en clair (sera haché côté backend).
    """
    mot_de_passe: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Mot de passe de l'utilisateur (minimum 8 caractères)",
        examples=["MyS3cur3P@ssw0rd"]
    )
    
    @field_validator('mot_de_passe')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Valide la robustesse du mot de passe :
        - Au moins 8 caractères
        - Au moins une majuscule
        - Au moins une minuscule
        - Au moins un chiffre
        """
        if len(v) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        if not any(c.isupper() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not any(c.islower() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        if not any(c.isdigit() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john.doe@example.com",
                "pseudo": "JohnDoe",
                "nom": "Doe",
                "prenom": "John",
                "mot_de_passe": "MyS3cur3P@ssw0rd"
            }
        }
    )


# ============================================
# MODÈLE UPDATE - Modification
# ============================================
class UserUpdate(BaseModel):
    """
    Modèle pour la mise à jour d'un utilisateur.
    Tous les champs sont optionnels pour permettre des mises à jour partielles.
    """
    email: Optional[EmailStr] = Field(
        None,
        description="Nouvelle adresse email"
    )
    pseudo: Optional[str] = Field(
        None,
        min_length=3,
        max_length=20,
        description="Nouveau pseudo"
    )
    nom: Optional[str] = Field(
        None,
        min_length=2,
        max_length=50,
        description="Nouveau nom"
    )
    prenom: Optional[str] = Field(
        None,
        min_length=2,
        max_length=50,
        description="Nouveau prénom"
    )
    mot_de_passe: Optional[str] = Field(
        None,
        min_length=8,
        max_length=100,
        description="Nouveau mot de passe"
    )
    actif: Optional[bool] = Field(
        None,
        description="Statut actif/inactif du compte"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "new.email@example.com",
                "pseudo": "NewPseudo"
            }
        }
    )


# ============================================
# MODÈLE RESPONSE - Réponse API
# ============================================
class UserResponse(UserBase):
    """
    Modèle pour la réponse API contenant les données d'un utilisateur.
    Inclut l'ID et les timestamps, mais PAS le mot de passe.
    """
    id: int = Field(
        ...,
        description="Identifiant unique de l'utilisateur"
    )
    actif: bool = Field(
        default=True,
        description="Indique si le compte est actif"
    )
    administrateur: bool = Field(
        default=False,
        description="Indique si l'utilisateur est administrateur"
    )
    created_at: datetime = Field(
        ...,
        description="Date de création du compte"
    )
    updated_at: datetime = Field(
        ...,
        description="Date de dernière modification du compte"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "john.doe@example.com",
                "pseudo": "JohnDoe",
                "nom": "Doe",
                "prenom": "John",
                "actif": True,
                "administrateur": False,
                "created_at": "2024-12-10T10:00:00",
                "updated_at": "2024-12-10T10:00:00"
            }
        }
    )


# ============================================
# MODÈLE LOGIN - Authentification
# ============================================
class UserLogin(BaseModel):
    """
    Modèle pour la connexion d'un utilisateur.
    Peut utiliser l'email OU le pseudo pour se connecter.
    """
    identifier: str = Field(
        ...,
        description="Email ou pseudo de l'utilisateur",
        examples=["john.doe@example.com", "JohnDoe"]
    )
    mot_de_passe: str = Field(
        ...,
        description="Mot de passe de l'utilisateur"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "identifier": "john.doe@example.com",
                "mot_de_passe": "MyS3cur3P@ssw0rd"
            }
        }
    )


# ============================================
# MODÈLE TOKEN - Réponse d'authentification
# ============================================
class Token(BaseModel):
    """
    Modèle pour la réponse après une authentification réussie.
    Contient le token JWT et le type de token.
    """
    access_token: str = Field(
        ...,
        description="Token JWT d'authentification"
    )
    token_type: str = Field(
        default="bearer",
        description="Type de token (toujours 'bearer')"
    )
    user: UserResponse = Field(
        ...,
        description="Informations de l'utilisateur connecté"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": "john.doe@example.com",
                    "pseudo": "JohnDoe",
                    "nom": "Doe",
                    "prenom": "John",
                    "actif": True,
                    "administrateur": False
                }
            }
        }
    )