# backend/routes/auth.py
# Routes d'authentification (inscription, connexion, profil)
# Endpoints REST pour la gestion de l'authentification utilisateur

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated

from database import get_db
from models.user import UserCreate, UserLogin, UserResponse, Token
from services import user_service
from utils.security import create_access_token, decode_access_token

# ============================================
# CONFIGURATION DU ROUTER
# ============================================
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Unauthorized - Invalid credentials"},
        403: {"description": "Forbidden - Account disabled"},
        409: {"description": "Conflict - User already exists"}
    }
)

# OAuth2 scheme pour la documentation Swagger
# tokenUrl doit correspondre à l'endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ============================================
# DÉPENDANCES
# ============================================
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Dépendance pour récupérer l'utilisateur actuel depuis le token JWT.
    
    Args:
        token (str): Token JWT depuis le header Authorization
        db (Session): Session de base de données
        
    Returns:
        UserResponse: Utilisateur authentifié
        
    Raises:
        HTTPException 401: Si le token est invalide ou expiré
        
    Utilisation dans une route:
        @router.get("/protected")
        def protected_route(current_user: UserResponse = Depends(get_current_user)):
            return {"user": current_user.username}
    """
    # Décodage du token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Récupération de l'email depuis le payload
    email: str = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Récupération de l'utilisateur en base
    user = user_service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Vérification que le compte est actif
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    return UserResponse.model_validate(user)


async def get_current_active_user(
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> UserResponse:
    """
    Dépendance pour vérifier que l'utilisateur est actif.
    Utilise get_current_user comme dépendance.
    
    Args:
        current_user (UserResponse): Utilisateur depuis get_current_user
        
    Returns:
        UserResponse: Utilisateur actif
        
    Raises:
        HTTPException 403: Si le compte est désactivé
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    return current_user


# ============================================
# ROUTES D'AUTHENTIFICATION
# ============================================
@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account and return an access token"
)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Token:
    """
    Inscription d'un nouvel utilisateur.
    
    Args:
        user_data (UserCreate): Données d'inscription validées
        db (Session): Session de base de données
        
    Returns:
        Token: Token JWT + informations utilisateur
        
    Raises:
        HTTPException 409: Si l'email ou le username existe déjà
        HTTPException 400: Si les données sont invalides
        
    Exemple de requête:
        POST /auth/register
        {
            "email": "john@example.com",
            "username": "JohnDoe",
            "first_name": "John",
            "last_name": "Doe",
            "password": "MyS3cur3P@ssw0rd"
        }
    """
    try:
        # Création de l'utilisateur
        db_user = user_service.create_user(db, user_data)
        
        # Génération du token JWT
        access_token = create_access_token(
            data={
                "sub": db_user.email,
                "user_id": db_user.id,
                "username": db_user.username
            }
        )
        
        # Conversion en modèle Pydantic pour la réponse
        user_response = UserResponse.model_validate(db_user)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except ValueError as e:
        # Email ou username déjà existant
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        # Erreur inattendue
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post(
    "/login",
    response_model=Token,
    summary="Login with email or username",
    description="Authenticate with email/username and password, returns access token"
)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
) -> Token:
    """
    Connexion d'un utilisateur existant.
    
    Args:
        user_credentials (UserLogin): Identifiant (email/username) + mot de passe
        db (Session): Session de base de données
        
    Returns:
        Token: Token JWT + informations utilisateur
        
    Raises:
        HTTPException 401: Si les identifiants sont incorrects
        HTTPException 403: Si le compte est désactivé
        
    Exemple de requête:
        POST /auth/login
        {
            "identifier": "john@example.com",  # ou "JohnDoe"
            "password": "MyS3cur3P@ssw0rd"
        }
    """
    # Authentification de l'utilisateur
    user = user_service.authenticate_user(
        db,
        user_credentials.identifier,
        user_credentials.password
    )
    
    if not user:
        # Credentials invalides (message volontairement générique pour sécurité)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Vérification que le compte est actif
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Génération du token JWT
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "username": user.username
        }
    )
    
    # Conversion en modèle Pydantic pour la réponse
    user_response = UserResponse.model_validate(user)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@router.post(
    "/login/form",
    response_model=Token,
    summary="Login with OAuth2 form (Swagger compatibility)",
    description="Alternative login endpoint compatible with Swagger UI",
    include_in_schema=False  # Caché de la doc principale
)
async def login_form(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> Token:
    """
    Endpoint de connexion compatible avec le formulaire OAuth2 de Swagger.
    Identique à /auth/login mais utilise OAuth2PasswordRequestForm.
    
    Note: Cet endpoint est principalement pour la compatibilité Swagger.
          Utilisez /auth/login pour les clients API normaux.
    """
    # Authentification (form_data.username peut être email ou username)
    user = user_service.authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Génération du token
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "username": user.username
        }
    )
    
    user_response = UserResponse.model_validate(user)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Returns the profile of the currently authenticated user"
)
async def get_me(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
) -> UserResponse:
    """
    Récupère le profil de l'utilisateur actuellement connecté.
    
    Args:
        current_user (UserResponse): Utilisateur depuis le token JWT
        
    Returns:
        UserResponse: Profil de l'utilisateur
        
    Exemple de requête:
        GET /auth/me
        Headers:
            Authorization: Bearer <token_jwt>
    """
    return current_user


@router.get(
    "/verify",
    summary="Verify JWT token validity",
    description="Checks if the provided JWT token is valid and not expired"
)
async def verify_token(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
) -> dict:
    """
    Vérifie la validité du token JWT.
    
    Args:
        current_user (UserResponse): Utilisateur depuis le token JWT
        
    Returns:
        dict: Statut de validation + infos utilisateur
        
    Exemple de requête:
        GET /auth/verify
        Headers:
            Authorization: Bearer <token_jwt>
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }


@router.post(
    "/logout",
    summary="Logout user",
    description="Logout the current user (client-side token invalidation)"
)
async def logout(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
) -> dict:
    """
    Déconnexion de l'utilisateur actuel.
    
    Note technique:
    Avec JWT stateless, le token reste techniquement valide jusqu'à expiration.
    Le logout est géré côté client en supprimant le token du stockage local.
    
    Cet endpoint confirme simplement la demande de déconnexion et permet
    de logger l'événement si nécessaire (audit, analytics).
    
    Args:
        current_user (UserResponse): Utilisateur authentifié
        
    Returns:
        dict: Message de confirmation
        
    Exemple de requête:
        POST /auth/logout
        Headers:
            Authorization: Bearer <token_jwt>
            
    Exemple de réponse:
        {
            "message": "Successfully logged out",
            "user_id": 1,
            "username": "john_doe"
        }
        
    Côté client (JavaScript):
        // Supprimer le token
        localStorage.removeItem('access_token');
        // ou
        sessionStorage.removeItem('access_token');
    """
    return {
        "message": "Successfully logged out",
        "user_id": current_user.id,
        "username": current_user.username
    }