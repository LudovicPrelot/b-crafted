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
        description="Email address of the user (unique)",
        examples=["john.doe@example.com"]
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        description="Username of the user (unique, between 3 and 20 characters)",
        examples=["JohnDoe"]
    )
    first_name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="First name of the user",
        examples=["John"]
    )
    last_name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Last name of the user",
        examples=["Doe"]
    )
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        Validates that username contains only alphanumeric characters and underscores.
        """
        if not v.replace('_', '').isalnum():
            raise ValueError('Username can only contain letters, numbers and underscores')
        return v


# ============================================
# MODÈLE CREATE - Inscription
# ============================================
class UserCreate(UserBase):
    """
    Model for user creation (registration).
    Contains the password in plain text (will be hashed on backend side).
    """
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="User password (minimum 8 characters)",
        examples=["MyS3cur3P@ssw0rd"]
    )
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validates password strength:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        """
        if len(v) < 8:
            raise ValueError('Password must contain at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john.doe@example.com",
                "username": "JohnDoe",
                "first_name": "John",
                "last_name": "Doe",
                "password": "MyS3cur3P@ssw0rd"
            }
        }
    )


# ============================================
# MODÈLE UPDATE - Modification
# ============================================
class UserUpdate(BaseModel):
    """
    Model for updating a user.
    All fields are optional to allow partial updates.
    """
    email: Optional[EmailStr] = Field(
        None,
        description="New email address"
    )
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=20,
        description="New username"
    )
    first_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=50,
        description="New first name"
    )
    last_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=50,
        description="New last name"
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=100,
        description="New password"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Active/inactive account status"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "new.email@example.com",
                "username": "NewUsername"
            }
        }
    )


# ============================================
# MODÈLE RESPONSE - Réponse API
# ============================================
class UserResponse(UserBase):
    """
    Model for API response containing user data.
    Includes ID, UUID and timestamps, but NOT the password.
    """
    id: int = Field(
        ...,
        description="Unique identifier of the user"
    )
    uuid: str = Field(
        ...,
        description="UUID of the user (for API security)"
    )
    is_active: bool = Field(
        default=True,
        description="Indicates if the account is active"
    )
    is_admin: bool = Field(
        default=False,
        description="Indicates if the user is administrator"
    )
    created_at: datetime = Field(
        ...,
        description="Account creation date"
    )
    updated_at: datetime = Field(
        ...,
        description="Last account modification date"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "uuid": "123e4567-e89b-12d3-a456-426614174000",
                "email": "john.doe@example.com",
                "username": "JohnDoe",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "is_admin": False,
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
    Model for user login.
    Can use email OR username to login.
    """
    identifier: str = Field(
        ...,
        description="Email or username of the user",
        examples=["john.doe@example.com", "JohnDoe"]
    )
    password: str = Field(
        ...,
        description="User password"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "identifier": "john.doe@example.com",
                "password": "MyS3cur3P@ssw0rd"
            }
        }
    )


# ============================================
# MODÈLE TOKEN - Réponse d'authentification
# ============================================
class Token(BaseModel):
    """
    Model for response after successful authentication.
    Contains JWT token and token type.
    """
    access_token: str = Field(
        ...,
        description="JWT authentication token"
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')"
    )
    user: UserResponse = Field(
        ...,
        description="Logged in user information"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "uuid": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "john.doe@example.com",
                    "username": "JohnDoe",
                    "first_name": "John",
                    "last_name": "Doe",
                    "is_active": True,
                    "is_admin": False
                }
            }
        }
    )