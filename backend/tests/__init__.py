# backend/tests/__init__.py
# Package des tests unitaires et d'intégration
# Ce fichier permet d'importer le module tests comme un package Python

"""
Package tests
=============

Contient tous les tests unitaires et d'intégration de l'application.

Organisation:
- conftest.py : Fixtures partagées (DB, client, users de test)
- test_security.py : Tests bcrypt + JWT
- test_user_service.py : Tests logique métier utilisateurs
- test_auth_routes.py : Tests endpoints authentification
- test_users_routes.py : Tests endpoints CRUD utilisateurs

Exécution des tests:
    # Tous les tests
    pytest tests/
    
    # Avec couverture
    pytest tests/ --cov=. --cov-report=html
    
    # Tests spécifiques
    pytest tests/test_security.py
    
    # Tests par marker
    pytest tests/ -m unit
    pytest tests/ -m integration

Markers disponibles:
    @pytest.mark.unit : Tests unitaires (logique métier)
    @pytest.mark.integration : Tests d'intégration (DB, API)
    @pytest.mark.slow : Tests lents (> 1 seconde)
    @pytest.mark.auth : Tests d'authentification
    @pytest.mark.crud : Tests CRUD
"""

__all__ = []