# backend/tests/test_security.py
# Tests unitaires pour les utilitaires de sécurité
# Teste le hachage bcrypt et la génération/validation JWT

import pytest
from datetime import timedelta
from utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    verify_token,
    is_token_expired,
    get_token_expiration_time
)


# ============================================
# TESTS HACHAGE BCRYPT
# ============================================
class TestPasswordHashing:
    """Tests pour le hachage et la vérification des mots de passe."""
    
    def test_hash_password_returns_string(self):
        """hash_password() doit retourner une chaîne de caractères."""
        password = "MyS3cur3P@ssw0rd"
        hashed = hash_password(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_hash_password_different_each_time(self):
        """Deux hachages du même mot de passe doivent être différents (salt)."""
        password = "MyS3cur3P@ssw0rd"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2
    
    def test_verify_password_correct(self):
        """verify_password() doit retourner True pour un mot de passe correct."""
        password = "MyS3cur3P@ssw0rd"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """verify_password() doit retourner False pour un mot de passe incorrect."""
        password = "MyS3cur3P@ssw0rd"
        wrong_password = "WrongP@ssw0rd"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty(self):
        """verify_password() doit retourner False pour un mot de passe vide."""
        password = "MyS3cur3P@ssw0rd"
        hashed = hash_password(password)
        
        assert verify_password("", hashed) is False
    
    def test_hash_special_characters(self):
        """Le hachage doit fonctionner avec des caractères spéciaux."""
        password = "P@$$w0rd!#%&*()_+-=[]{}|;:',.<>?/"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True


# ============================================
# TESTS JWT
# ============================================
class TestJWTTokens:
    """Tests pour la génération et validation des tokens JWT."""
    
    def test_create_access_token_returns_string(self):
        """create_access_token() doit retourner une chaîne JWT."""
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        # Un JWT contient 3 parties séparées par des points
        assert token.count(".") == 2
    
    def test_decode_access_token_valid(self):
        """decode_access_token() doit retourner le payload pour un token valide."""
        data = {"sub": "test@example.com", "user_id": 1, "username": "testuser"}
        token = create_access_token(data)
        
        payload = decode_access_token(token)
        
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1
        assert payload["username"] == "testuser"
        assert "exp" in payload  # Champ expiration ajouté automatiquement
    
    def test_decode_access_token_invalid(self):
        """decode_access_token() doit retourner None pour un token invalide."""
        invalid_token = "invalid.token.here"
        
        payload = decode_access_token(invalid_token)
        
        assert payload is None
    
    def test_decode_access_token_expired(self):
        """decode_access_token() doit retourner None pour un token expiré."""
        data = {"sub": "test@example.com"}
        # Token expirant dans le passé (-1 seconde)
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        payload = decode_access_token(token)
        
        assert payload is None
    
    def test_verify_token_valid(self):
        """verify_token() doit retourner True pour un token valide."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        assert verify_token(token) is True
    
    def test_verify_token_with_expected_sub(self):
        """verify_token() doit vérifier le champ 'sub' si fourni."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        assert verify_token(token, expected_sub="test@example.com") is True
        assert verify_token(token, expected_sub="wrong@example.com") is False
    
    def test_verify_token_invalid(self):
        """verify_token() doit retourner False pour un token invalide."""
        invalid_token = "invalid.token.here"
        
        assert verify_token(invalid_token) is False
    
    def test_is_token_expired_valid(self):
        """is_token_expired() doit retourner False pour un token valide."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        assert is_token_expired(token) is False
    
    def test_is_token_expired_expired(self):
        """is_token_expired() doit retourner True pour un token expiré."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        assert is_token_expired(token) is True
    
    def test_is_token_expired_invalid(self):
        """is_token_expired() doit retourner True pour un token invalide."""
        invalid_token = "invalid.token.here"
        
        assert is_token_expired(invalid_token) is True


# ============================================
# TESTS UTILITAIRES
# ============================================
class TestSecurityUtils:
    """Tests pour les fonctions utilitaires de sécurité."""
    
    def test_get_token_expiration_time(self):
        """get_token_expiration_time() doit retourner un entier > 0."""
        expiration = get_token_expiration_time()
        
        assert isinstance(expiration, int)
        assert expiration > 0
    
    def test_token_contains_expiration(self):
        """Un token JWT doit contenir un champ 'exp' (expiration)."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        payload = decode_access_token(token)
        
        assert "exp" in payload
        assert isinstance(payload["exp"], (int, float))
        assert payload["exp"] > 0


# ============================================
# TESTS D'INTÉGRATION SÉCURITÉ
# ============================================
class TestSecurityIntegration:
    """Tests d'intégration pour le workflow complet de sécurité."""
    
    def test_full_password_workflow(self):
        """Test du workflow complet : hash → verify → success."""
        original_password = "MyS3cur3P@ssw0rd123"
        
        # 1. Hachage
        hashed = hash_password(original_password)
        
        # 2. Vérification correcte
        assert verify_password(original_password, hashed) is True
        
        # 3. Vérification incorrecte
        assert verify_password("WrongPassword", hashed) is False
    
    def test_full_jwt_workflow(self):
        """Test du workflow complet : create → decode → verify → success."""
        user_data = {
            "sub": "test@example.com",
            "user_id": 1,
            "username": "testuser"
        }
        
        # 1. Création du token
        token = create_access_token(user_data)
        
        # 2. Décodage du token
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == user_data["sub"]
        assert payload["user_id"] == user_data["user_id"]
        
        # 3. Vérification du token
        assert verify_token(token) is True
        assert verify_token(token, expected_sub=user_data["sub"]) is True
        
        # 4. Vérification non-expiration
        assert is_token_expired(token) is False
    
    def test_authentication_simulation(self):
        """Simule un workflow d'authentification complet."""
        # Données utilisateur
        email = "user@example.com"
        plain_password = "UserP@ssw0rd123"
        
        # 1. Inscription : hachage du mot de passe
        hashed_password = hash_password(plain_password)
        
        # 2. Connexion : vérification du mot de passe
        is_authenticated = verify_password(plain_password, hashed_password)
        assert is_authenticated is True
        
        # 3. Génération du token JWT
        token_data = {"sub": email, "user_id": 1}
        access_token = create_access_token(token_data)
        
        # 4. Vérification du token (requête protégée)
        payload = decode_access_token(access_token)
        assert payload is not None
        assert payload["sub"] == email
        
        # 5. Accès autorisé
        assert verify_token(access_token, expected_sub=email) is True