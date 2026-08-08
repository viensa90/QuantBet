from typing import Optional

# Mapeo de nombres de mercado de la API a nombre canónico
MARKET_MAP = {
    'h2h': 'moneyline',
    'moneyline': 'moneyline',
    'head_to_head': 'moneyline',
    'spreads': 'spread',
    'totals': 'totals',
    'over_under': 'totals',
    'both_teams_to_score': 'btts',
}

def normalize_market(oddsapi_market: str) -> Optional[str]:
    """Devuelve el nombre canónico del mercado o None si no se reconoce."""
    return MARKET_MAP.get(oddsapi_market.lower(), None)

def get_outcome_name(oddsapi_outcome_name: str) -> str:
    """
    Traduce nombres de outcomes de la API a nombres legibles.
    Ej: 'Over' -> 'Over 2.5'? En la API el nombre ya incluye la línea.
    """
    return oddsapi_outcome_name