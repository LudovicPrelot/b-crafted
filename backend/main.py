# backend/main.py
# Point d'entrée principal de l'API B'Craft'D
# Ce fichier configure FastAPI et les routes de base

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
import sys

# Import de la fonction de test de connexion DB
from database import check_db_connection, get_db_info

# Import de la fonction d'initialisation de la base de données
from scripts.init_db import init_database

# Import des routes
from routes.auth import router as auth_router

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
    allow_origins=[settings.API_BASE_URL],
    # Autorise l'envoi de cookies et credentials
    allow_credentials=True,
    # Autorise toutes les méthodes HTTP (GET, POST, PUT, DELETE, etc.)
    allow_methods=["*"],
    # Autorise tous les headers HTTP
    allow_headers=["*"],
)


# ============================================
# ÉVÉNEMENTS DE DÉMARRAGE / ARRÊT
# ============================================
@app.on_event("startup")
async def startup_event():
    """
    Événement exécuté au démarrage de l'application.
    Initialise la base de données via init_database().
    """
    print("\n" + "=" * 60)
    print("🚀 B'Craft'D API - Démarrage")
    print("=" * 60 + "\n")
    
    # Appel de la fonction d'initialisation de la base de données
    success = init_database()
    
    if not success:
        print("\n❌ ERREUR : Échec de l'initialisation de la base de données")
        print("💡 L'API ne peut pas démarrer sans base de données")
        sys.exit(1)
    
    print("=" * 60)
    print("✅ B'Craft'D API démarrée avec succès !")
    print("📚 Documentation : " + settings.API_BASE_URL + "/docs")
    print("=" * 60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Événement exécuté à l'arrêt de l'application.
    Nettoie les ressources si nécessaire.
    """
    print("\n👋 B'Craft'D API - Arrêt en cours...")


# ============================================
# INCLUSION DES ROUTES
# ============================================
# Routes d'authentification (/auth)
app.include_router(auth_router)


# ============================================
# ROUTES DE BASE
# ============================================
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
        "docs": "/docs",  # Lien vers la documentation Swagger
        "endpoints": {
            "auth": "/auth",
            "health": "/health"
        }
    }


# Route health check - utilisée par Docker pour vérifier la santé du service
@app.get("/health")
async def health_check():
    """
    Endpoint de health check.
    Vérifie que l'API est opérationnelle et que la connexion DB fonctionne.
    
    Returns:
        dict: Status de santé du service et de la base de données
    """
    # Test de la connexion PostgreSQL
    db_connected = check_db_connection()
    
    # Récupération des infos de connexion (sans mot de passe)
    db_info = get_db_info() if db_connected else None
    
    return {
        "status": "healthy" if db_connected else "degraded",
        "service": "backend",
        "database": {
            "status": "connected" if db_connected else "disconnected",
            "type": "PostgreSQL",
            "info": db_info
        }
    }


# Point d'entrée si le fichier est exécuté directement (sans Docker)
# Utile pour le développement local sans Docker
if __name__ == "__main__":
    import uvicorn
    
    # Démarre le serveur Uvicorn
    # host="0.0.0.0" : écoute sur toutes les interfaces réseau
    # port=5000 : port d'écoute (défini dans .env)
    # reload=True : active le hot-reload en développement
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)