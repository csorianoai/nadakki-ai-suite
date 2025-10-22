"""
Agent Compatibility Helper
Convierte dict → Pydantic sin romper código existente
"""

from typing import Any, Dict, Type, TypeVar
from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

def coerce_to_model(Model: Type[T], data: Any) -> T:
    """
    Convierte dict a modelo Pydantic de forma segura
    
    Args:
        Model: Clase Pydantic target
        data: Dict o modelo Pydantic
        
    Returns:
        Instancia del modelo
        
    Raises:
        ValidationError: Si no se puede convertir
    """
    # Si ya es el modelo correcto, devolverlo
    if isinstance(data, Model):
        return data
    
    # Si es dict, intentar conversión directa
    if isinstance(data, dict):
        try:
            return Model(**data)
        except ValidationError as e:
            # Intentar con wrapper "data" si existe
            if "data" in data and isinstance(data["data"], dict):
                try:
                    return Model(**data["data"])
                except ValidationError:
                    pass
            
            # Log el error y re-raise
            logger.warning(f"Cannot coerce to {Model.__name__}: {e}")
            raise
    
    # Si no es dict ni modelo, intentar convertir
    try:
        return Model(**data)
    except Exception as e:
        logger.error(f"Failed to coerce {type(data)} to {Model.__name__}: {e}")
        raise ValueError(f"Cannot convert {type(data)} to {Model.__name__}")

def safe_dict_access(data: Any, *keys, default=None):
    """
    Acceso seguro a dict anidado
    
    Args:
        data: Dict o objeto
        keys: Secuencia de keys
        default: Valor por defecto
        
    Returns:
        Valor encontrado o default
        
    Example:
        safe_dict_access(data, 'attributes', 'credit_score', default=500)
    """
    current = data
    
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        elif hasattr(current, key):
            current = getattr(current, key)
        else:
            return default
        
        if current is None:
            return default
    
    return current if current is not None else default
