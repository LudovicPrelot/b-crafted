# app/main.py
# Point d'entrée principal de l'API B'Craft'D
# Ce fichier minimal permet de tester que le container fonctionne

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Création de l'instance FastAPI
# title : nom affiché dans la documentation Swagger
# description : description du projet
# version : version actuelle de l'API
app = FastAPI(
    title="B'Craft'D API",
    description="API REST pour le jeu de crafting réaliste B'Craft'D",
    version="0.1.0"
)

# Configuration CORS (Cross-Origin Resource Sharing)
# Permet au frontend React (port 5173) de communiquer avec l'API (port 8000)
app.add_middleware(
    CORSMiddleware,
    # Liste des origines autorisées (frontend en développement)
    allow_origins=[os.getenv("API_BASE_URL")],
    # Autorise l'envoi de cookies et credentials
    allow_credentials=True,
    # Autorise toutes les méthodes HTTP (GET, POST, PUT, DELETE, etc.)
    allow_methods=["*"],
    # Autorise tous les headers HTTP
    allow_headers=["*"],
)


# Route racine - endpoint de base pour tester que l'API fonctionne
@app.get("/")
async def root():
    """
    Endpoint racine de l'API.
    Retourne un message de bienvenue et des informations de base.
    
    Returns:
        dict: Message de bienvenue et status
    """
    return {
        "message": "Bienvenue sur l'API B'Craft'D !",
        "status": "running",
        "version": "0.1.0",
        "docs": "/docs"  # Lien vers la documentation Swagger
    }


# Route health check - utilisée par Docker pour vérifier la santé du service
@app.get("/health")
async def health_check():
    """
    Endpoint de health check.
    Vérifie que l'API est opérationnelle.
    
    Returns:
        dict: Status de santé du service
    """
    return {
        "status": "healthy",
        "service": "backend",
        "database": "not_connected"  # TODO: vérifier connexion DB quand elle sera configurée
    }


# Point d'entrée si le fichier est exécuté directement (sans Docker)
# Utile pour le développement local sans Docker
if __name__ == "__main__":
    import uvicorn
    
    # Démarre le serveur Uvicorn
    # host="0.0.0.0" : écoute sur toutes les interfaces réseau
    # port=8000 : port d'écoute
    # reload=True : active le hot-reload en développement
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)