# backend/config/settings.py
# Configuration centralisée avec autoload depuis backend/.env

from pathlib import Path
from dotenv import load_dotenv
import os

# ============================================
# CHARGEMENT AUTOMATIQUE DU FICHIER .env
# ============================================
# Localisation du fichier .env (backend/.env)
env_file = Path(__file__).resolve().parent.parent / ".env"

# Charge le fichier .env s'il existe
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Variables chargées depuis : {env_file}")
else:
    print(f"⚠️  Fichier .env non trouvé : {env_file}")


# ============================================
# CLASSE SETTINGS - ACCÈS DYNAMIQUE
# ============================================
class Settings:
    """
    Accès dynamique aux variables d'environnement depuis backend/.env.
    
    Utilisation:
        from config import settings
        user = settings.POSTGRES_USER
        password = settings.POSTGRES_PASSWORD
        url = settings["API_BASE_URL"]
    
    Les variables du .env sont chargées automatiquement.
    Pas besoin de les déclarer dans le code.
    """
    
    def __getattr__(self, name: str):
        """
        Récupère les variables d'environnement dynamiquement.
        
        Permet: settings.POSTGRES_USER
        """
        value = os.getenv(name)
        if value is None:
            raise AttributeError(
                f"❌ Variable d'environnement '{name}' non trouvée. "
                f"Vérifiez le fichier backend/.env"
            )
        return value
    
    def __getitem__(self, key: str):
        """
        Récupère les variables d'environnement via la syntaxe dictionnaire.
        
        Permet: settings["POSTGRES_USER"]
        """
        return self.__getattr__(key)
    
    def get(self, key: str, default=None):
        """
        Récupère une variable avec valeur par défaut.
        
        Permet: settings.get("POSTGRES_USER", "default_user")
        """
        return os.getenv(key, default)


# Instance unique de settings
settings = Settings()
