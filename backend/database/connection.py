# backend/database/connection.py
# Configuration de la connexion PostgreSQL avec SQLAlchemy
# Gestion des sessions et du connection pooling

import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from typing import Generator

# ============================================
# VARIABLES D'ENVIRONNEMENT
# ============================================
# Récupération des variables d'environnement pour la connexion PostgreSQL
POSTGRES_USER = os.getenv("POSTGRES_USER", "bcraftd_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "bcraftd_password")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "bcraftd")

# Construction de l'URL de connexion PostgreSQL
# Format : postgresql://user:password@host:port/database
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# ============================================
# CONFIGURATION SQLALCHEMY ENGINE
# ============================================
# Création du moteur SQLAlchemy avec options de performance
engine = create_engine(
    DATABASE_URL,
    # Connection pooling : réutilisation des connexions pour performance
    poolclass=QueuePool,
    pool_size=5,  # Nombre de connexions permanentes dans le pool
    max_overflow=10,  # Nombre de connexions supplémentaires autorisées
    pool_pre_ping=True,  # Vérifie la connexion avant utilisation (évite les connexions mortes)
    pool_recycle=3600,  # Recycle les connexions après 1 heure
    echo=False,  # Si True, affiche toutes les requêtes SQL (utile en debug)
)

# ============================================
# SESSION FACTORY
# ============================================
# Création de la factory de sessions
# SessionLocal sera utilisé pour créer des sessions DB dans les routes
SessionLocal = sessionmaker(
    autocommit=False,  # Transactions manuelles (plus de contrôle)
    autoflush=False,  # Flush manuel des objets vers la DB
    bind=engine,  # Lie la session au moteur PostgreSQL
)

# ============================================
# BASE DECLARATIVE
# ============================================
# Base pour tous les modèles SQLAlchemy (schemas)
# Tous les modèles hériteront de cette classe
Base = declarative_base()


# ============================================
# DEPENDENCY INJECTION FASTAPI
# ============================================
def get_db() -> Generator:
    """
    Fonction de dépendance pour obtenir une session de base de données.
    
    Utilisée dans les routes FastAPI avec Depends(get_db).
    La session est automatiquement fermée après utilisation grâce au yield.
    
    Yields:
        Session: Session SQLAlchemy pour effectuer des requêtes DB
        
    Exemple d'utilisation dans une route:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================
# GESTION DES ÉVÉNEMENTS
# ============================================
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """
    Événement déclenché lors de l'établissement d'une connexion.
    Utile pour configurer des paramètres spécifiques par connexion.
    """
    # Exemple : forcer l'encodage UTF-8
    # dbapi_conn.set_client_encoding('utf8')
    pass


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """
    Événement déclenché quand une connexion est extraite du pool.
    Utile pour logger ou surveiller l'utilisation des connexions.
    """
    pass


# ============================================
# FONCTIONS UTILITAIRES
# ============================================
def init_db():
    """
    Initialise la base de données en créant toutes les tables.
    À appeler au démarrage de l'application.
    
    Note: En production, utiliser Alembic pour les migrations
    au lieu de cette fonction.
    """
    # Import tous les modèles avant de créer les tables
    # pour que Base.metadata les connaisse
    # from backend.schemas import user, character, profession, resource, recipe
    
    Base.metadata.create_all(bind=engine)


def check_db_connection() -> bool:
    """
    Vérifie que la connexion à PostgreSQL est fonctionnelle.
    
    Returns:
        bool: True si la connexion réussit, False sinon
        
    Exemple d'utilisation dans la route /health:
        @app.get("/health")
        def health():
            db_status = "connected" if check_db_connection() else "disconnected"
            return {"database": db_status}
    """
    try:
        # Teste la connexion avec une requête simple
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Erreur de connexion PostgreSQL : {e}")
        return False


# ============================================
# INFORMATIONS DE CONNEXION (DEBUG)
# ============================================
def get_db_info() -> dict:
    """
    Retourne les informations de connexion (sans le mot de passe).
    Utile pour le debugging et les logs.
    
    Returns:
        dict: Informations de connexion PostgreSQL
    """
    return {
        "host": POSTGRES_HOST,
        "port": POSTGRES_PORT,
        "database": POSTGRES_DB,
        "user": POSTGRES_USER,
        "url": f"postgresql://{POSTGRES_USER}:***@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    }