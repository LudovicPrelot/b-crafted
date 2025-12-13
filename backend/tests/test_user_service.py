# backend/tests/test_user_service.py
# Tests unitaires pour le service utilisateur
# Teste la logique métier (CRUD, authentification)

import pytest
from sqlalchemy.orm import Session
from models.user import UserCreate, UserUpdate
from services import user_service
from utils.security import verify_password


# ============================================
# TESTS CRÉATION UTILISATEUR
# ============================================
@pytest.mark.unit
class TestCreateUser:
    """Tests pour la création d'utilisateurs."""
    
    def test_create_user_success(self, db: Session, test_user_data: dict):
        """Création d'un utilisateur doit réussir avec des données valides."""
        user_create = UserCreate(**test_user_data)
        user = user_service.create_user(db, user_create)
        
        assert user.id is not None
        assert user.uuid is not None
        assert user.email == test_user_data["email"]
        assert user.username == test_user_data["username"]
        assert user.first_name == test_user_data["first_name"]
        assert user.last_name == test_user_data["last_name"]
        assert user.is_active is True
        assert user.is_admin is False
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_create_user_password_hashed(self, db: Session, test_user_data: dict):
        """Le mot de passe doit être haché, pas stocké en clair."""
        user_create = UserCreate(**test_user_data)
        user = user_service.create_user(db, user_create)
        
        # Le mot de passe ne doit PAS être identique au mot de passe en clair
        assert user.password != test_user_data["password"]
        
        # Le mot de passe doit être vérifiable avec bcrypt
        assert verify_password(test_user_data["password"], user.password)
    
    def test_create_user_duplicate_email(self, db: Session, test_user_data: dict):
        """Création avec email existant doit échouer."""
        user_create = UserCreate(**test_user_data)
        user_service.create_user(db, user_create)
        
        # Tentative de création avec même email
        with pytest.raises(ValueError, match="Email .* already exists"):
            user_service.create_user(db, user_create)
    
    def test_create_user_duplicate_username(self, db: Session, test_user_data: dict):
        """Création avec username existant doit échouer."""
        user_create = UserCreate(**test_user_data)
        user_service.create_user(db, user_create)
        
        # Tentative de création avec même username mais email différent
        test_user_data["email"] = "different@example.com"
        user_create2 = UserCreate(**test_user_data)
        
        with pytest.raises(ValueError, match="Username .* already exists"):
            user_service.create_user(db, user_create2)


# ============================================
# TESTS RÉCUPÉRATION UTILISATEUR
# ============================================
@pytest.mark.unit
class TestGetUser:
    """Tests pour la récupération d'utilisateurs."""
    
    def test_get_user_by_id(self, db: Session, test_user):
        """Récupération par ID doit fonctionner."""
        user = user_service.get_user_by_id(db, test_user.id)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
    
    def test_get_user_by_id_not_found(self, db: Session):
        """Récupération avec ID inexistant doit retourner None."""
        user = user_service.get_user_by_id(db, 999999)
        
        assert user is None
    
    def test_get_user_by_email(self, db: Session, test_user):
        """Récupération par email doit fonctionner."""
        user = user_service.get_user_by_email(db, test_user.email)
        
        assert user is not None
        assert user.email == test_user.email
    
    def test_get_user_by_username(self, db: Session, test_user):
        """Récupération par username doit fonctionner."""
        user = user_service.get_user_by_username(db, test_user.username)
        
        assert user is not None
        assert user.username == test_user.username
    
    def test_get_user_by_identifier_email(self, db: Session, test_user):
        """get_user_by_identifier doit fonctionner avec email."""
        user = user_service.get_user_by_identifier(db, test_user.email)
        
        assert user is not None
        assert user.email == test_user.email
    
    def test_get_user_by_identifier_username(self, db: Session, test_user):
        """get_user_by_identifier doit fonctionner avec username."""
        user = user_service.get_user_by_identifier(db, test_user.username)
        
        assert user is not None
        assert user.username == test_user.username
    
    def test_get_users_pagination(self, db: Session, sample_users):
        """get_users doit supporter la pagination."""
        # Récupérer les 3 premiers
        users_page1 = user_service.get_users(db, skip=0, limit=3)
        assert len(users_page1) == 3
        
        # Récupérer les 2 suivants
        users_page2 = user_service.get_users(db, skip=3, limit=3)
        assert len(users_page2) == 2
        
        # Les utilisateurs ne doivent pas se chevaucher
        assert users_page1[0].id != users_page2[0].id
    
    def test_count_users(self, db: Session, sample_users):
        """count_users doit retourner le nombre total."""
        count = user_service.count_users(db)
        
        assert count == 5  # sample_users crée 5 utilisateurs


# ============================================
# TESTS MISE À JOUR UTILISATEUR
# ============================================
@pytest.mark.unit
class TestUpdateUser:
    """Tests pour la mise à jour d'utilisateurs."""
    
    def test_update_user_success(self, db: Session, test_user):
        """Mise à jour des champs doit fonctionner."""
        update_data = UserUpdate(
            first_name="Updated",
            last_name="Name"
        )
        
        updated = user_service.update_user(db, test_user.id, update_data)
        
        assert updated is not None
        assert updated.first_name == "Updated"
        assert updated.last_name == "Name"
        assert updated.email == test_user.email  # Inchangé
    
    def test_update_user_password(self, db: Session, test_user):
        """Mise à jour du mot de passe doit le hacher."""
        new_password = "NewP@ssw0rd123"
        update_data = UserUpdate(password=new_password)
        
        updated = user_service.update_user(db, test_user.id, update_data)
        
        # Le nouveau mot de passe doit être haché
        assert updated.password != new_password
        assert verify_password(new_password, updated.password)
    
    def test_update_user_duplicate_email(self, db: Session, test_user, test_admin):
        """Mise à jour avec email existant doit échouer."""
        update_data = UserUpdate(email=test_admin.email)
        
        with pytest.raises(ValueError, match="Email .* already exists"):
            user_service.update_user(db, test_user.id, update_data)
    
    def test_update_user_not_found(self, db: Session):
        """Mise à jour d'utilisateur inexistant doit retourner None."""
        update_data = UserUpdate(first_name="Test")
        updated = user_service.update_user(db, 999999, update_data)
        
        assert updated is None


# ============================================
# TESTS SUPPRESSION UTILISATEUR
# ============================================
@pytest.mark.unit
class TestDeleteUser:
    """Tests pour la suppression d'utilisateurs."""
    
    def test_soft_delete_user(self, db: Session, test_user):
        """Soft delete doit désactiver le compte."""
        success = user_service.delete_user(db, test_user.id, soft_delete=True)
        
        assert success is True
        
        # L'utilisateur doit toujours exister mais être inactif
        user = user_service.get_user_by_id(db, test_user.id)
        assert user is not None
        assert user.is_active is False
    
    def test_hard_delete_user(self, db: Session, test_user):
        """Hard delete doit supprimer définitivement."""
        success = user_service.delete_user(db, test_user.id, soft_delete=False)
        
        assert success is True
        
        # L'utilisateur ne doit plus exister
        user = user_service.get_user_by_id(db, test_user.id)
        assert user is None
    
    def test_delete_user_not_found(self, db: Session):
        """Suppression d'utilisateur inexistant doit retourner False."""
        success = user_service.delete_user(db, 999999)
        
        assert success is False


# ============================================
# TESTS AUTHENTIFICATION
# ============================================
@pytest.mark.unit
@pytest.mark.auth
class TestAuthentication:
    """Tests pour l'authentification utilisateur."""
    
    def test_authenticate_user_success_email(self, db: Session, test_user, test_user_data: dict):
        """Authentification avec email + password correct doit réussir."""
        user = user_service.authenticate_user(
            db,
            test_user_data["email"],
            test_user_data["password"]
        )
        
        assert user is not None
        assert user.id == test_user.id
    
    def test_authenticate_user_success_username(self, db: Session, test_user, test_user_data: dict):
        """Authentification avec username + password correct doit réussir."""
        user = user_service.authenticate_user(
            db,
            test_user_data["username"],
            test_user_data["password"]
        )
        
        assert user is not None
        assert user.id == test_user.id
    
    def test_authenticate_user_wrong_password(self, db: Session, test_user):
        """Authentification avec mauvais password doit échouer."""
        user = user_service.authenticate_user(
            db,
            test_user.email,
            "WrongPassword123"
        )
        
        assert user is None
    
    def test_authenticate_user_not_found(self, db: Session):
        """Authentification avec email inexistant doit échouer."""
        user = user_service.authenticate_user(
            db,
            "notfound@example.com",
            "SomePassword123"
        )
        
        assert user is None
    
    def test_authenticate_user_inactive(self, db: Session, test_user, test_user_data: dict):
        """Authentification d'un compte inactif doit échouer."""
        # Désactiver le compte
        test_user.is_active = False
        db.commit()
        
        user = user_service.authenticate_user(
            db,
            test_user_data["email"],
            test_user_data["password"]
        )
        
        assert user is None


# ============================================
# TESTS ACTIVATION/DÉSACTIVATION
# ============================================
@pytest.mark.unit
class TestActivation:
    """Tests pour l'activation/désactivation de comptes."""
    
    def test_deactivate_user(self, db: Session, test_user):
        """Désactivation d'un compte doit fonctionner."""
        success = user_service.deactivate_user(db, test_user.id)
        
        assert success is True
        
        user = user_service.get_user_by_id(db, test_user.id)
        assert user.is_active is False
    
    def test_activate_user(self, db: Session, test_user):
        """Activation d'un compte doit fonctionner."""
        # Désactiver d'abord
        test_user.is_active = False
        db.commit()
        
        # Réactiver
        success = user_service.activate_user(db, test_user.id)
        
        assert success is True
        
        user = user_service.get_user_by_id(db, test_user.id)
        assert user.is_active is True
    
    def test_activate_user_not_found(self, db: Session):
        """Activation d'utilisateur inexistant doit retourner False."""
        success = user_service.activate_user(db, 999999)
        
        assert success is False