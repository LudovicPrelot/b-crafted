# backend/models/__init__.py
# Module des modèles Pydantic pour la validation des données
# Ce fichier permet d'importer le module models comme un package Python

"""
Module models
=============

Contient les modèles Pydantic pour la validation des données API.

Les modèles Pydantic servent à :
- Valider les données entrantes (requêtes API)
- Valider les données sortantes (réponses API)
- Générer automatiquement la documentation OpenAPI/Swagger
- Assurer la cohérence des types de données

Contenu futur :
- user.py : Modèles User (UserCreate, UserUpdate, UserResponse)
- character.py : Modèles Character
- profession.py : Modèles Profession
- resource.py : Modèles Resource
- recipe.py : Modèles Recipe
"""

# Pour l'instant, le fichier est vide
# Les imports seront ajoutés au fur et à mesure de la création des fichiers

__all__ = []