# backend/schemas/base.py
# Configuration de base SQLAlchemy pour tous les schémas
# Définit la base declarative et les mixins communs

from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import declarative_base
from datetime import datetime

# Base declarative pour tous les modèles SQLAlchemy
# Tous les schémas hériteront de cette classe
Base = declarative_base()


class TimestampMixin:
    """
    Mixin pour ajouter automatiquement les colonnes de timestamp.
    À utiliser dans tous les modèles qui nécessitent created_at et updated_at.
    
    Utilisation :
        class User(Base, TimestampMixin):
            __tablename__ = "users"
            ...
    """
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="Date de création de l'enregistrement"
    )
    
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Date de dernière modification de l'enregistrement"
    )