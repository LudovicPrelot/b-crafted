# backend/utils/security.py
# Utilitaires de sécurité pour l'authentification
# Gestion du hachage des mots de passe et des tokens JWT

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from config import settings

# ============================================
# CONFIGURATION BCRYPT
# ============================================
# Context pour le hachage des mots de passe avec bcrypt
# bcrypt est recommandé pour les mots de passe (résistant aux attaques GPU)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================
# CONFIGURATION JWT
# ============================================
# Récupération des variables d'environnement
SECRET_KEY = settings.get("SECRET_KEY", "your-secret-key-change-me-in-production")
ALGORITHM = settings.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.get("JWT_EXPIRATION", 30))


# ============================================
# FONCTIONS DE HACHAGE DE MOT DE PASSE
# ============================================
def hash_password(password: str) -> str:
    """
    Hache un mot de passe en clair avec bcrypt.
    
    Args:
        password (str): Mot de passe en clair
        
    Returns:
        str: Mot de passe haché (stockable en DB)
        
    Exemple:
        hashed = hash_password("MyS3cur3P@ssw0rd")
        # Résultat: "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36..."
    """
    # IMPORTANT: bcrypt a une limite de 72 octets
    # Troncature manuelle à 72 octets max pour éviter l'erreur bcrypt
    truncated = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(truncated)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe en clair correspond au hash stocké.
    
    Args:
        plain_password (str): Mot de passe en clair (saisi par l'utilisateur)
        hashed_password (str): Hash stocké en base de données
        
    Returns:
        bool: True si le mot de passe est correct, False sinon
        
    Exemple:
        is_valid = verify_password("MyS3cur3P@ssw0rd", stored_hash)
        if is_valid:
            # Authentification réussie
    """
    # IMPORTANT: bcrypt a une limite de 72 octets
    # Troncature manuelle à 72 octets max pour correspondre au hash stocké
    truncated = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(truncated, hashed_password)


# ============================================
# FONCTIONS JWT
# ============================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Génère un token JWT pour l'authentification.
    
    Args:
        data (dict): Données à encoder dans le token (ex: {"sub": "user@example.com"})
        expires_delta (timedelta, optional): Durée de validité custom du token
        
    Returns:
        str: Token JWT encodé
        
    Exemple:
        token = create_access_token({"sub": user.email, "user_id": user.id})
        # Résultat: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        
    Note:
        - Le champ "sub" (subject) doit contenir l'identifiant unique de l'utilisateur
        - Par défaut, le token expire après ACCESS_TOKEN_EXPIRE_MINUTES (30 min)
    """
    to_encode = data.copy()
    
    # Calcul de l'expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Ajout du champ "exp" (expiration) au payload JWT
    to_encode.update({"exp": expire})
    
    # Encodage du token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Décode et vérifie un token JWT.
    
    Args:
        token (str): Token JWT à décoder
        
    Returns:
        dict: Payload du token si valide, None si invalide ou expiré
        
    Exemple:
        payload = decode_access_token(token)
        if payload:
            user_email = payload.get("sub")
            user_id = payload.get("user_id")
        else:
            # Token invalide ou expiré
            
    Note:
        - Vérifie automatiquement l'expiration du token
        - Vérifie la signature avec SECRET_KEY
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # Token invalide, expiré ou signature incorrecte
        return None


def verify_token(token: str, expected_sub: Optional[str] = None) -> bool:
    """
    Vérifie qu'un token JWT est valide et correspond à un utilisateur.
    
    Args:
        token (str): Token JWT à vérifier
        expected_sub (str, optional): Email/identifiant attendu dans le token
        
    Returns:
        bool: True si le token est valide, False sinon
        
    Exemple:
        if verify_token(token, user.email):
            # Token valide et correspond à l'utilisateur
        else:
            # Token invalide
    """
    payload = decode_access_token(token)
    if not payload:
        return False
    
    # Vérification optionnelle du "sub" (identifiant utilisateur)
    if expected_sub:
        token_sub = payload.get("sub")
        return token_sub == expected_sub
    
    return True


# ============================================
# FONCTIONS UTILITAIRES
# ============================================
def get_token_expiration_time() -> int:
    """
    Retourne la durée de validité des tokens en minutes.
    
    Returns:
        int: Nombre de minutes avant expiration du token
    """
    return ACCESS_TOKEN_EXPIRE_MINUTES


def is_token_expired(token: str) -> bool:
    """
    Vérifie si un token JWT est expiré.
    
    Args:
        token (str): Token JWT à vérifier
        
    Returns:
        bool: True si expiré, False sinon
    """
    payload = decode_access_token(token)
    if not payload:
        return True  # Token invalide = considéré comme expiré
    
    exp = payload.get("exp")
    if not exp:
        return True
    
    return datetime.utcnow() > datetime.fromtimestamp(exp)