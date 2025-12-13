# backend/tests/test_users_routes.py
# Tests d'intégration pour les routes CRUD utilisateurs
# Teste les endpoints /users/* avec permissions

import pytest
from fastapi.testclient import TestClient


# ============================================
# TESTS COMPTEUR (GET /users/count)
# ============================================
@pytest.mark.integration
@pytest.mark.crud
class TestUsersCount:
    """Tests pour l'endpoint GET /users/count (public)."""
    
    def test_count_users_public(self, client: TestClient, sample_users):
        """Compteur doit être accessible sans authentification."""
        response = client.get("/users/count")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total" in data
        assert data["total"] == 5  # sample_users crée 5 utilisateurs


# ============================================
# TESTS LISTE (GET /users)
# ============================================
@pytest.mark.integration
@pytest.mark.crud
class TestListUsers:
    """Tests pour l'endpoint GET /users (admin only)."""
    
    def test_list_users_admin_success(self, client: TestClient, admin_headers: dict, sample_users):
        """Liste paginée doit être accessible aux admins."""
        response = client.get("/users?page=1&per_page=3", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "metadata" in data
        assert len(data["items"]) == 3
        assert data["metadata"]["page"] == 1
        assert data["metadata"]["per_page"] == 3
        assert data["metadata"]["total"] == 6  # 5 sample + 1 admin
    
    def test_list_users_pagination(self, client: TestClient, admin_headers: dict, sample_users):
        """Pagination doit fonctionner correctement."""
        # Page 1
        response1 = client.get("/users?page=1&per_page=2", headers=admin_headers)
        data1 = response1.json()
        
        # Page 2
        response2 = client.get("/users?page=2&per_page=2", headers=admin_headers)
        data2 = response2.json()
        
        assert len(data1["items"]) == 2
        assert len(data2["items"]) == 2
        assert data1["items"][0]["id"] != data2["items"][0]["id"]
        assert data1["metadata"]["has_next"] is True
        assert data2["metadata"]["has_prev"] is True
    
    def test_list_users_non_admin_forbidden(self, client: TestClient, auth_headers: dict):
        """Liste doit être interdite aux non-admins."""
        response = client.get("/users", headers=auth_headers)
        
        assert response.status_code == 403
    
    def test_list_users_no_auth(self, client: TestClient):
        """Liste doit être interdite sans authentification."""
        response = client.get("/users")
        
        assert response.status_code == 401


# ============================================
# TESTS MON PROFIL (GET /users/me)
# ============================================
@pytest.mark.integration
@pytest.mark.crud
class TestGetMyProfile:
    """Tests pour l'endpoint GET /users/me."""
    
    def test_get_my_profile_success(self, client: TestClient, auth_headers: dict, test_user):
        """Récupération de son propre profil doit réussir."""
        response = client.get("/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email


# ============================================
# TESTS DÉTAIL UTILISATEUR (GET /users/{id})
# ============================================
@pytest.mark.integration
@pytest.mark.crud
class TestGetUser:
    """Tests pour l'endpoint GET /users/{id}."""
    
    def test_get_user_owner(self, client: TestClient, auth_headers: dict, test_user):
        """Propriétaire doit pouvoir voir son profil."""
        response = client.get(f"/users/{test_user.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
    
    def test_get_user_admin(self, client: TestClient, admin_headers: dict, test_user):
        """Admin doit pouvoir voir n'importe quel profil."""
        response = client.get(f"/users/{test_user.id}", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
    
    def test_get_user_other_forbidden(self, client: TestClient, auth_headers: dict, test_admin):
        """Non-admin ne doit pas voir le profil d'un autre."""
        response = client.get(f"/users/{test_admin.id}", headers=auth_headers)
        
        assert response.status_code == 403
    
    def test_get_user_not_found(self, client: TestClient, admin_headers: dict):
        """Récupération d'utilisateur inexistant doit échouer."""
        response = client.get("/users/999999", headers=admin_headers)
        
        assert response.status_code == 404


# ============================================
# TESTS MISE À JOUR (PUT /users/{id})
# ============================================
@pytest.mark.integration
@pytest.mark.crud
class TestUpdateUser:
    """Tests pour l'endpoint PUT /users/{id}."""
    
    def test_update_user_owner(self, client: TestClient, auth_headers: dict, test_user):
        """Propriétaire doit pouvoir modifier son profil."""
        response = client.put(
            f"/users/{test_user.id}",
            headers=auth_headers,
            json={"first_name": "Updated", "last_name": "Name"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
    
    def test_update_user_admin(self, client: TestClient, admin_headers: dict, test_user):
        """Admin doit pouvoir modifier n'importe quel profil."""
        response = client.put(
            f"/users/{test_user.id}",
            headers=admin_headers,
            json={"first_name": "AdminUpdated"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "AdminUpdated"
    
    def test_update_user_other_forbidden(self, client: TestClient, auth_headers: dict, test_admin):
        """Non-admin ne doit pas modifier le profil d'un autre."""
        response = client.put(
            f"/users/{test_admin.id}",
            headers=auth_headers,
            json={"first_name": "Hacked"}
        )
        
        assert response.status_code == 403
    
    def test_update_user_duplicate_email(self, client: TestClient, auth_headers: dict, test_user, test_admin):
        """Mise à jour avec email existant doit échouer."""
        response = client.put(
            f"/users/{test_user.id}",
            headers=auth_headers,
            json={"email": test_admin.email}
        )
        
        assert response.status_code == 409


# ============================================
# TESTS SUPPRESSION (DELETE /users/{id})
# ============================================
@pytest.mark.integration
@pytest.mark.crud
class TestDeleteUser:
    """Tests pour l'endpoint DELETE /users/{id}."""
    
    def test_delete_user_admin(self, client: TestClient, admin_headers: dict, test_user):
        """Admin doit pouvoir supprimer un utilisateur."""
        response = client.delete(f"/users/{test_user.id}", headers=admin_headers)
        
        assert response.status_code == 204
        
        # Vérifier que l'utilisateur est désactivé (soft delete)
        get_response = client.get(f"/users/{test_user.id}", headers=admin_headers)
        assert get_response.status_code == 200
        assert get_response.json()["is_active"] is False
    
    def test_delete_user_non_admin_forbidden(self, client: TestClient, auth_headers: dict, test_admin):
        """Non-admin ne doit pas pouvoir supprimer."""
        response = client.delete(f"/users/{test_admin.id}", headers=auth_headers)
        
        assert response.status_code == 403
    
    def test_delete_user_self_forbidden(self, client: TestClient, admin_headers: dict, test_admin):
        """Admin ne doit pas pouvoir se supprimer lui-même."""
        response = client.delete(f"/users/{test_admin.id}", headers=admin_headers)
        
        assert response.status_code == 400


# ============================================
# TESTS ACTIVATION/DÉSACTIVATION
# ============================================
@pytest.mark.integration
@pytest.mark.crud
class TestActivateDeactivate:
    """Tests pour les endpoints POST /users/{id}/activate et /deactivate."""
    
    def test_deactivate_user_admin(self, client: TestClient, admin_headers: dict, test_user):
        """Admin doit pouvoir désactiver un utilisateur."""
        response = client.post(f"/users/{test_user.id}/deactivate", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
    
    def test_activate_user_admin(self, client: TestClient, db, admin_headers: dict, test_user):
        """Admin doit pouvoir activer un utilisateur."""
        # Désactiver d'abord
        test_user.is_active = False
        db.commit()
        
        response = client.post(f"/users/{test_user.id}/activate", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True
    
    def test_deactivate_user_non_admin_forbidden(self, client: TestClient, auth_headers: dict, test_admin):
        """Non-admin ne doit pas pouvoir désactiver."""
        response = client.post(f"/users/{test_admin.id}/deactivate", headers=auth_headers)
        
        assert response.status_code == 403
    
    def test_deactivate_self_forbidden(self, client: TestClient, admin_headers: dict, test_admin):
        """Admin ne doit pas pouvoir se désactiver lui-même."""
        response = client.post(f"/users/{test_admin.id}/deactivate", headers=admin_headers)
        
        assert response.status_code == 400


# ============================================
# TESTS PERMISSIONS COMPLEXES
# ============================================
@pytest.mark.integration
@pytest.mark.crud
class TestPermissions:
    """Tests des règles de permissions complexes."""
    
    def test_user_can_update_own_profile(self, client: TestClient, auth_headers: dict, test_user):
        """Utilisateur peut modifier son propre profil."""
        response = client.put(
            f"/users/{test_user.id}",
            headers=auth_headers,
            json={"first_name": "SelfUpdated"}
        )
        
        assert response.status_code == 200
    
    def test_user_cannot_update_others(self, client: TestClient, auth_headers: dict, test_admin):
        """Utilisateur ne peut pas modifier le profil d'un autre."""
        response = client.put(
            f"/users/{test_admin.id}",
            headers=auth_headers,
            json={"first_name": "NotAllowed"}
        )
        
        assert response.status_code == 403
    
    def test_admin_can_update_anyone(self, client: TestClient, admin_headers: dict, test_user):
        """Admin peut modifier n'importe quel profil."""
        response = client.put(
            f"/users/{test_user.id}",
            headers=admin_headers,
            json={"first_name": "AdminModified"}
        )
        
        assert response.status_code == 200