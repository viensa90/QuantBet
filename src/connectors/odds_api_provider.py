"""
Proveedor de datos: The Odds API (v4)
Documentación: https://the-odds-api.com/liveapi/guides/v4/
"""
import requests
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from src.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Outcome:
    """Una cuota individual para un resultado específico de un bookmaker."""
    bookmaker: str
    name: str          # Ej: "Home", "Over 2.5", "Draw"
    price: float


@dataclass
class AggregatedEvent:
    """
    Evento con todas las cuotas de todos los bookmakers disponibles,
    listo para ser analizado por el motor de arbitraje.
    """
    event_name: str
    sport: str
    market: str                     # Nombre normalizado del mercado (ej. "h2h", "totals")
    outcomes: List[Outcome]         # Lista de cuotas de todos los bookmakers para este mercado
    timestamp: Optional[str] = None


class OddsAPIProvider:
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get("key") or config.get("api_key")
        if not self.api_key:
            raise ValueError("No se encontró 'key' ni 'api_key' en la configuración de odds_api")
        self.base_url = config.get("base_url", "https://api.the-odds-api.com/v4")
        self.sports = config.get("sports", [
            "soccer_spain_la_liga",
            "soccer_epl"                         # ← clave corregida
        ])
        self.regions = config.get("regions", "eu")
        self.markets = config.get("markets", "h2h,totals,spreads")
        self.bookmakers = config.get("bookmakers", None)

    def get_events(self) -> List[AggregatedEvent]:
        aggregated_events = []
        for sport in self.sports:
            try:
                sport_events = self._fetch_sport(sport)
                aggregated_events.extend(sport_events)   # ← usar extend
            except Exception as e:
                logger.error("Error obteniendo eventos para %s: %s", sport, e)
        return aggregated_events

    def _fetch_sport(self, sport: str) -> List[AggregatedEvent]:
        url = f"{self.base_url}/sports/{sport}/odds"
        params = {
            "apiKey": self.api_key,
            "regions": self.regions,
            "markets": self.markets,
            "dateFormat": "iso",
            "oddsFormat": "decimal",
        }
        if self.bookmakers:
            params["bookmakers"] = self.bookmakers

        logger.info("Consultando Odds API: %s", url)
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        events = []
        for game in data:
            parsed = self._parse_game(sport, game)
            if parsed:
                events.extend(parsed)   # ← parsed es lista de AggregatedEvent
        return events

    def _parse_game(self, sport: str, game: dict) -> Optional[List[AggregatedEvent]]:
        try:
            event_name = f"{game['home_team']} vs {game['away_team']}"
            bookmakers_data = game.get("bookmakers", [])
            outcomes_by_market = {}

            for bk in bookmakers_data:
                bookmaker_name = bk["title"]
                for market in bk.get("markets", []):
                    market_key = market["key"]
                    outcomes_by_market.setdefault(market_key, [])
                    for oc in market.get("outcomes", []):
                        outcomes_by_market[market_key].append(
                            Outcome(
                                bookmaker=bookmaker_name,
                                name=oc["name"],
                                price=oc["price"]
                            )
                        )

            aggregated = []
            for market_key, outcomes_list in outcomes_by_market.items():
                aggregated.append(
                    AggregatedEvent(
                        event_name=event_name,
                        sport=sport,
                        market=market_key,
                        outcomes=outcomes_list,
                        timestamp=game.get("commence_time")
                    )
                )
            return aggregated

        except Exception as e:
            logger.warning("Error parseando juego: %s", e)
            return None