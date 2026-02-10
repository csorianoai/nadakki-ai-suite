"""Google Ads Integration Layer - NADAKKI AI Suite"""
import sys
import os
from pathlib import Path

# Setup paths
CURRENT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = CURRENT_DIR.parent.parent.parent
MVP_ROOT = PROJECT_ROOT / 'nadakki-google-ads-mvp'

# Agregar rutas necesarias
sys.path.insert(0, str(MVP_ROOT))
sys.path.insert(0, str(MVP_ROOT / 'agents' / 'marketing'))
sys.path.insert(0, str(MVP_ROOT / 'core'))

# Importar agentes Google Ads
from google_ads_budget_pacing_agent import GoogleAdsBudgetPacingIA
from google_ads_strategist_agent import GoogleAdsStrategistIA
from rsa_ad_copy_generator_agent import RSAAdCopyGeneratorIA
from search_terms_cleaner_agent import SearchTermsCleanerIA
from orchestrator_agent import OrchestratorIA

__all__ = [
    'GoogleAdsBudgetPacingIA',
    'GoogleAdsStrategistIA',
    'RSAAdCopyGeneratorIA',
    'SearchTermsCleanerIA',
    'OrchestratorIA',
]
