"""
Google Ads Configuration Module
Centraliza configuración y creación de clientes
"""

import os
import sys
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Importar factory correctamente
try:
    # Agregar MVP al path
    mvp_path = os.path.join(os.path.dirname(__file__), '..', '..', 'nadakki-google-ads-mvp')
    if mvp_path not in sys.path:
        sys.path.insert(0, mvp_path)
    
    from core.google_ads.client_factory import GoogleAdsClientFactory
    logger.info("✅ GoogleAdsClientFactory importado del MVP")
    
except ImportError as e:
    logger.error(f"⚠️ No se pudo importar GoogleAdsClientFactory: {e}")
    GoogleAdsClientFactory = None

__all__ = ['GoogleAdsClientFactory']
