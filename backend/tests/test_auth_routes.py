# backend/tests/test_auth_routes.py
# Tests d'intégration pour les routes d'authentification
# Teste les endpoints /auth/* (register, login, me, verify)

import pytest
from fastapi.testclient import TestClient


# ============================================
# TESTS INSCRIPTION (POST /auth/register)
# ============================================
@pytest.mark.integration
@pytest.mark.auth
class TestRegister:
    """Tests pour l'endpoint POST /auth/register."""
    
    def test_register_success(self, client: TestClient):
        """Inscription avec données valides doit réussir."""
        response = client.post("/auth/register", json={
            "email": "newuser@example.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "password": "NewP@ssw0rd123"
        })
        
        assert response.status_code == 201
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["username"] == "newuser"
        assert "password" not in data["user"]  # Ne doit jamais être retourné
    
    def test_register_duplicate_email(self, client: TestClient, test_user):
        """Inscription avec email existant doit échouer."""
        response = client.post("/auth/register", json={
            "email": test_user.email,  # Email existant
            "username": "differentuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "TestP@ssw0rd123"
        })
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()
    
    def test_register_duplicate_username(self, client: TestClient, test_user):
        """Inscription avec username existant doit échouer."""
        response = client.post("/auth/register", json={
            "email": "different@example.com",
            "username": test_user.username,  # Username existant
            "first_name": "Test",
            "last_name": "User",
            "password": "TestP@ssw0rd123"
        })
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, client: TestClient):
        """Inscription avec email invalide doit échouer."""
        response = client.post("/auth/register", json={
            "email": "not-an-email",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "TestP@ssw0rd123"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_register_weak_password(self, client: TestClient):
        """Inscription avec mot de passe faible doit échouer."""
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "weak"  # Pas de majuscule, pas de chiffre, trop court
        })
        
        assert response.status_code == 422


# ============================================
# TESTS CONNEXION (POST /auth/login)
# ============================================
@pytest.mark.integration
@pytest.mark.auth
class TestLogin:
    """Tests pour l'endpoint POST /auth/login."""
    
    def test_login_success_with_email(self, client: TestClient, test_user, test_user_data: dict):
        """Connexion avec email doit réussir."""
        response = client.post("/auth/login", json={
            "identifier": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == test_user_data["email"]
    
    def test_login_success_with_username(self, client: TestClient, test_user, test_user_data: dict):
        """Connexion avec username doit réussir."""
        response = client.post("/auth/login", json={
            "identifier": test_user_data["username"],
            "password": test_user_data["password"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["user"]["username"] == test_user_data["username"]
    
    def test_login_wrong_password(self, client: TestClient, test_user):
        """Connexion avec mauvais mot de passe doit échouer."""
        response = client.post("/auth/login", json={
            "identifier": test_user.email,
            "password": "WrongPassword123"
        })
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_user_not_found(self, client: TestClient):
        """Connexion avec utilisateur inexistant doit échouer."""
        response = client.post("/auth/login", json={
            "identifier": "notfound@example.com",
            "password": "SomePassword123"
        })
        
        assert response.status_code == 401
    
    def test_login_inactive_user(self, client: TestClient, db, test_user, test_user_data: dict):
        """Connexion avec compte inactif doit échouer."""
        # Désactiver le compte
        test_user.is_active = False
        db.commit()
        
        response = client.post("/auth/login", json={
            "identifier": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        assert response.status_code == 403
        assert "disabled" in response.json()["detail"].lower()


# ============================================
# TESTS PROFIL (GET /auth/me)
# ============================================
@pytest.mark.integration
@pytest.mark.auth
class TestGetMe:
    """Tests pour l'endpoint GET /auth/me."""
    
    def test_get_me_success(self, client: TestClient, auth_headers: dict, test_user):
        """Récupération du profil avec token valide doit réussir."""
        response = client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert "password" not in data
    
    def test_get_me_no_token(self, client: TestClient):
        """Récupération du profil sans token doit échouer."""
        response = client.get("/auth/me")
        
        assert response.status_code == 401
    
    def test_get_me_invalid_token(self, client: TestClient):
        """Récupération du profil avec token invalide doit échouer."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_get_me_inactive_user(self, client: TestClient, db, auth_headers: dict, test_user):
        """Récupération du profil avec compte inactif doit échouer."""
        # Désactiver le compte
        test_user.is_active = False
        db.commit()
        
        response = client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == 403


# ============================================
# TESTS VÉRIFICATION TOKEN (GET /auth/verify)
# ============================================
@pytest.mark.integration
@pytest.mark.auth
class TestVerifyToken:
    """Tests pour l'endpoint GET /auth/verify."""
    
    def test_verify_token_success(self, client: TestClient, auth_headers: dict, test_user):
        """Vérification d'un token valide doit réussir."""
        response = client.get("/auth/verify", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] is True
        assert data["user_id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
    
    def test_verify_token_invalid(self, client: TestClient):
        """Vérification d'un token invalide doit échouer."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/auth/verify", headers=headers)
        
        assert response.status_code == 401


# ============================================
# TESTS DÉCONNEXION (POST /auth/logout)
# ============================================
@pytest.mark.integration
@pytest.mark.auth
class TestLogout:
    """Tests pour l'endpoint POST /auth/logout."""
    
    def test_logout_success(self, client: TestClient, auth_headers: dict, test_user):
        """Déconnexion avec token valide doit réussir."""
        response = client.post("/auth/logout", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "Successfully logged out"
        assert data["user_id"] == test_user.id
        assert data["username"] == test_user.username
    
    def test_logout_no_token(self, client: TestClient):
        """Déconnexion sans token doit échouer."""
        response = client.post("/auth/logout")
        
        assert response.status_code == 401
    
    def test_logout_invalid_token(self, client: TestClient):
        """Déconnexion avec token invalide doit échouer."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.post("/auth/logout", headers=headers)
        
        assert response.status_code == 401
    
    def test_logout_inactive_user(self, client: TestClient, db, auth_headers: dict, test_user):
        """Déconnexion avec compte inactif doit échouer."""
        # Désactiver le compte
        test_user.is_active = False
        db.commit()
        
        response = client.post("/auth/logout", headers=auth_headers)
        
        assert response.status_code == 403


# ============================================
# TESTS WORKFLOW COMPLET
# ============================================
@pytest.mark.integration
@pytest.mark.auth
class TestAuthWorkflow:
    """Tests du workflow complet d'authentification."""
    
    def test_full_workflow_register_login_me(self, client: TestClient):
        """Test du workflow complet : inscription → connexion → profil."""
        # 1. Inscription
        register_data = {
            "email": "workflow@example.com",
            "username": "workflowuser",
            "first_name": "Work",
            "last_name": "Flow",
            "password": "WorkP@ssw0rd123"
        }
        register_response = client.post("/auth/register", json=register_data)
        assert register_response.status_code == 201
        
        register_token = register_response.json()["access_token"]
        
        # 2. Connexion
        login_response = client.post("/auth/login", json={
            "identifier": register_data["email"],
            "password": register_data["password"]
        })
        assert login_response.status_code == 200
        
        login_token = login_response.json()["access_token"]
        
        # 3. Récupération du profil avec les 2 tokens
        headers_register = {"Authorization": f"Bearer {register_token}"}
        headers_login = {"Authorization": f"Bearer {login_token}"}
        
        me_response1 = client.get("/auth/me", headers=headers_register)
        me_response2 = client.get("/auth/me", headers=headers_login)
        
        assert me_response1.status_code == 200
        assert me_response2.status_code == 200
        assert me_response1.json()["email"] == register_data["email"]
        assert me_response2.json()["email"] == register_data["email"]