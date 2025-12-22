"""
Ecosistema Marketing
Generado automáticamente
"""

# Imports automáticos
from .minimalformia import Minimalformia, create_agent as create_minimalformia
from .fidelizedprofileia import Fidelizedprofileia, create_agent as create_fidelizedprofileia
from .cashofferfilteria import Cashofferfilteria, create_agent as create_cashofferfilteria
from .contactqualityia import Contactqualityia, create_agent as create_contactqualityia
from .geosegmentationia import Geosegmentationia, create_agent as create_geosegmentationia
from .productaffinityia import Productaffinityia, create_agent as create_productaffinityia
from .conversioncohortia import Conversioncohortia, create_agent as create_conversioncohortia
from .abtestingimpactia import Abtestingimpactia, create_agent as create_abtestingimpactia
from .socialpostgeneratoria import Socialpostgeneratoria, create_agent as create_socialpostgeneratoria
from .videoreelautogenia import Videoreelautogenia, create_agent as create_videoreelautogenia
from .influencermatchia import Influencermatchia, create_agent as create_influencermatchia
from .contentviralityia import Contentviralityia, create_agent as create_contentviralityia
from .brandsentimentia import Brandsentimentia, create_agent as create_brandsentimentia
from .competitorintelligenceia import Competitorintelligenceia, create_agent as create_competitorintelligenceia

AGENTS_REGISTRY = {
    'Minimalformia': create_minimalformia,
    'Fidelizedprofileia': create_fidelizedprofileia,
    'Cashofferfilteria': create_cashofferfilteria,
    'Contactqualityia': create_contactqualityia,
    'Geosegmentationia': create_geosegmentationia,
    'Productaffinityia': create_productaffinityia,
    'Conversioncohortia': create_conversioncohortia,
    'Abtestingimpactia': create_abtestingimpactia,
    'Socialpostgeneratoria': create_socialpostgeneratoria,
    'Videoreelautogenia': create_videoreelautogenia,
    'Influencermatchia': create_influencermatchia,
    'Contentviralityia': create_contentviralityia,
    'Brandsentimentia': create_brandsentimentia,
    'Competitorintelligenceia': create_competitorintelligenceia,
}

__all__ = [
    'Minimalformia',
    'Fidelizedprofileia',
    'Cashofferfilteria',
    'Contactqualityia',
    'Geosegmentationia',
    'Productaffinityia',
    'Conversioncohortia',
    'Abtestingimpactia',
    'Socialpostgeneratoria',
    'Videoreelautogenia',
    'Influencermatchia',
    'Contentviralityia',
    'Brandsentimentia',
    'Competitorintelligenceia',
    "AGENTS_REGISTRY"
]