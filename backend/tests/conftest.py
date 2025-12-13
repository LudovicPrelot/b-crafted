# backend/tests/conftest.py
# Fixtures pytest partagées entre tous les tests
# Fournit des objets réutilisables (DB, client API, users de test)

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from main import app
from database.connection import get_db, Base
from models.user import UserCreate
from services import user_service
from utils.security import create_access_token

# ============================================
# CONFIGURATION BASE DE DONNÉES DE TEST
# ============================================
# Utilisation de SQLite en mémoire pour les tests (plus rapide)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Création de l'engine de test
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Pool statique pour SQLite en mémoire
)

# Session factory pour les tests
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


# ============================================
# FIXTURES DE BASE DE DONNÉES
# ============================================
@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """
    Fixture qui fournit une session de base de données de test.
    Crée toutes les tables avant chaque test et les supprime après.
    
    Scope: function (nouvelle DB pour chaque test)
    
    Yields:
        Session: Session SQLAlchemy pour le test
    """
    # Création de toutes les tables
    Base.metadata.create_all(bind=test_engine)
    
    # Création d'une session
    db_session = TestingSessionLocal()
    
    try:
        yield db_session
    finally:
        # Nettoyage
        db_session.close()
        # Suppression de toutes les tables
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    Fixture qui fournit un client de test FastAPI.
    Utilise la base de données de test au lieu de la vraie DB.
    
    Args:
        db (Session): Session de test depuis la fixture db
        
    Yields:
        TestClient: Client pour effectuer des requêtes HTTP de test
        
    Exemple d'utilisation:
        def test_example(client):
            response = client.get("/")
            assert response.status_code == 200
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    # Override de la dépendance get_db
    app.dependency_overrides[get_db] = override_get_db
    
    # Création du client de test
    with TestClient(app) as test_client:
        yield test_client
    
    # Nettoyage des overrides
    app.dependency_overrides.clear()


# ============================================
# FIXTURES UTILISATEURS DE TEST
# ============================================
@pytest.fixture(scope="function")
def test_user_data() -> dict:
    """
    Fixture qui fournit les données d'un utilisateur de test.
    
    Returns:
        dict: Données utilisateur de test
    """
    return {
        "email": "test@example.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "password": "TestP@ssw0rd123"
    }


@pytest.fixture(scope="function")
def test_user(db: Session, test_user_data: dict):
    """
    Fixture qui crée un utilisateur de test en base de données.
    
    Args:
        db (Session): Session de test
        test_user_data (dict): Données utilisateur de test
        
    Returns:
        User: Utilisateur créé en DB
    """
    user_create = UserCreate(**test_user_data)
    user = user_service.create_user(db, user_create)
    return user


@pytest.fixture(scope="function")
def test_admin_data() -> dict:
    """
    Fixture qui fournit les données d'un admin de test.
    
    Returns:
        dict: Données admin de test
    """
    return {
        "email": "admin@example.com",
        "username": "adminuser",
        "first_name": "Admin",
        "last_name": "User",
        "password": "AdminP@ssw0rd123"
    }


@pytest.fixture(scope="function")
def test_admin(db: Session, test_admin_data: dict):
    """
    Fixture qui crée un admin de test en base de données.
    
    Args:
        db (Session): Session de test
        test_admin_data (dict): Données admin de test
        
    Returns:
        User: Admin créé en DB avec is_admin=True
    """
    user_create = UserCreate(**test_admin_data)
    user = user_service.create_user(db, user_create)
    
    # Promotion en admin
    user.is_admin = True
    db.commit()
    db.refresh(user)
    
    return user


# ============================================
# FIXTURES TOKENS JWT
# ============================================
@pytest.fixture(scope="function")
def test_user_token(test_user) -> str:
    """
    Fixture qui génère un token JWT pour l'utilisateur de test.
    
    Args:
        test_user: Utilisateur de test depuis la fixture
        
    Returns:
        str: Token JWT valide pour l'utilisateur
        
    Exemple d'utilisation:
        def test_protected_route(client, test_user_token):
            headers = {"Authorization": f"Bearer {test_user_token}"}
            response = client.get("/auth/me", headers=headers)
            assert response.status_code == 200
    """
    token_data = {
        "sub": test_user.email,
        "user_id": test_user.id,
        "username": test_user.username
    }
    return create_access_token(token_data)


@pytest.fixture(scope="function")
def test_admin_token(test_admin) -> str:
    """
    Fixture qui génère un token JWT pour l'admin de test.
    
    Args:
        test_admin: Admin de test depuis la fixture
        
    Returns:
        str: Token JWT valide pour l'admin
    """
    token_data = {
        "sub": test_admin.email,
        "user_id": test_admin.id,
        "username": test_admin.username
    }
    return create_access_token(token_data)


# ============================================
# FIXTURES HEADERS HTTP
# ============================================
@pytest.fixture(scope="function")
def auth_headers(test_user_token: str) -> dict:
    """
    Fixture qui fournit les headers HTTP avec authentification user.
    
    Args:
        test_user_token (str): Token JWT utilisateur
        
    Returns:
        dict: Headers HTTP avec Authorization Bearer
    """
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture(scope="function")
def admin_headers(test_admin_token: str) -> dict:
    """
    Fixture qui fournit les headers HTTP avec authentification admin.
    
    Args:
        test_admin_token (str): Token JWT admin
        
    Returns:
        dict: Headers HTTP avec Authorization Bearer
    """
    return {"Authorization": f"Bearer {test_admin_token}"}


# ============================================
# FIXTURES UTILITAIRES
# ============================================
@pytest.fixture(scope="function")
def sample_users(db: Session) -> list:
    """
    Fixture qui crée plusieurs utilisateurs de test en DB.
    Utile pour tester la pagination et les listes.
    
    Args:
        db (Session): Session de test
        
    Returns:
        list: Liste d'utilisateurs créés
    """
    users = []
    for i in range(5):
        user_data = UserCreate(
            email=f"user{i}@example.com",
            username=f"user{i}",
            first_name=f"User{i}",
            last_name=f"Test{i}",
            password="TestP@ssw0rd123"
        )
        user = user_service.create_user(db, user_data)
        users.append(user)
    
    return users