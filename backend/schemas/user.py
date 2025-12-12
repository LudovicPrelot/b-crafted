# backend/schemas/user.py
# Schéma SQLAlchemy pour la table users
# Définit la structure de la table utilisateurs dans PostgreSQL

from sqlalchemy import Column, Integer, String, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """
    Table users - Stocke les informations des utilisateurs.
    
    Cette table contient tous les utilisateurs du système B'Craft'D,
    avec leurs informations d'authentification et de profil.
    
    Relations futures :
    - characters : Un utilisateur peut avoir plusieurs personnages
    """
    
    __tablename__ = "users"
    
    # ============================================
    # CLÉS PRIMAIRES ET IDENTIFIANTS
    # ============================================
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Identifiant unique auto-incrémenté"
    )
    
    uuid = Column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid.uuid4,
        comment="Identifiant UUID unique pour sécurité API"
    )
    
    # ============================================
    # AUTHENTIFICATION
    # ============================================
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Adresse email de l'utilisateur (unique, utilisée pour connexion)"
    )
    
    username = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Pseudo de l'utilisateur (unique, utilisé pour connexion)"
    )
    
    password = Column(
        String(255),
        nullable=False,
        comment="Mot de passe haché avec bcrypt"
    )
    
    # ============================================
    # INFORMATIONS PERSONNELLES
    # ============================================
    first_name = Column(
        String(50),
        nullable=False,
        comment="Prénom de l'utilisateur"
    )
    
    last_name = Column(
        String(50),
        nullable=False,
        comment="Nom de famille de l'utilisateur"
    )
    
    # ============================================
    # STATUTS ET PERMISSIONS
    # ============================================
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Indique si le compte utilisateur est actif"
    )
    
    is_admin = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Indique si l'utilisateur a les droits administrateur"
    )
    
    # ============================================
    # TIMESTAMPS
    # ============================================
    # created_at et updated_at sont ajoutés via TimestampMixin
    
    # ============================================
    # INDEX ET CONTRAINTES
    # ============================================
    __table_args__ = (
        # Index sur UUID pour recherche rapide par UUID
        Index('idx_users_uuid', 'uuid'),
        
        # Index sur email (déjà unique, mais index pour performance)
        Index('idx_users_email', 'email'),
        
        # Index sur username (déjà unique, mais index pour performance)
        Index('idx_users_username', 'username'),
        
        # Index composite pour recherche par nom complet
        Index('idx_users_fullname', 'first_name', 'last_name'),
        
        # Index sur is_active pour filtrer les utilisateurs actifs
        Index('idx_users_is_active', 'is_active'),
    )
    
    def __repr__(self):
        """
        Représentation string de l'objet User.
        Utile pour le debugging.
        """
        return f"<User(id={self.id}, uuid={self.uuid}, username='{self.username}', email='{self.email}')>"
    
    def __str__(self):
        """
        Représentation lisible de l'utilisateur.
        """
        return f"{self.first_name} {self.last_name} (@{self.username})"