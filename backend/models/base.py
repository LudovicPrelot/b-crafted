# backend/models/base.py
# Modèles Pydantic de base communs à tous les modèles
# Utilise Pydantic v2 avec ConfigDict

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class BaseModelConfig(BaseModel):
    """
    Modèle de base pour tous les modèles Pydantic.
    Configure les paramètres communs à tous les modèles.
    """
    model_config = ConfigDict(
        # from_attributes=True permet de créer un modèle Pydantic
        # depuis un objet SQLAlchemy (anciennement orm_mode=True en Pydantic v1)
        from_attributes=True,
        
        # Validation stricte des types
        strict=False,
        
        # Autorise les champs supplémentaires (ignore les champs non définis)
        extra='ignore',
        
        # Active la validation lors de l'assignation de valeurs
        validate_assignment=True,
        
        # Utilise les enums par valeur plutôt que par nom
        use_enum_values=True,
    )


class TimestampMixin(BaseModel):
    """
    Mixin pour les champs de timestamp (dates de création/modification).
    À utiliser dans les modèles Response qui incluent ces champs.
    """
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class IDMixin(BaseModel):
    """
    Mixin pour le champ ID.
    À utiliser dans les modèles Response qui incluent un ID.
    """
    id: int  # Utilise int pour auto-increment, ou str pour UUID
    
    model_config = ConfigDict(from_attributes=True)