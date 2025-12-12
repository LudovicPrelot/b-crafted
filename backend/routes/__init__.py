# backend/routes/__init__.py
# Module des routes API (endpoints)
# Ce fichier permet d'importer le module routes comme un package Python

"""
Module routes
=============

Contient les routes API (endpoints) de l'application FastAPI.

Les routes définissent :
- Les URLs accessibles (ex: /users, /characters, /resources)
- Les méthodes HTTP (GET, POST, PUT, DELETE)
- Les paramètres et le body des requêtes
- Les réponses renvoyées par l'API

Contenu futur :
- health.py : Routes de health check (/health, /status)
- users.py : Routes CRUD utilisateurs (/users)
- characters.py : Routes CRUD personnages (/characters)
- professions.py : Routes professions (/professions)
- resources.py : Routes ressources (/resources)
- recipes.py : Routes recettes (/recipes)
- auth.py : Routes authentification (à venir en V1)
"""

# Pour l'instant, le fichier est vide
# Les imports seront ajoutés au fur et à mesure de la création des fichiers

__all__ = []