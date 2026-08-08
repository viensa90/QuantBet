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
    name: str          # Nombre del resultado (ej. "Home", "Over 2.5", "Draw")
    price: float


@dataclass
class AggregatedEvent:
    """
    Evento con las mejores cuotas de todos los bookmakers disponibles,
    listo para ser analizado por el motor de arbitraje.
    """
    event_name: str
    sport: str
    market: str                     # Nombre normalizado del mercado (ej. "h2h", "totals")
    outcomes: List[Outcome]         # Lista de todas las cuotas de todos los bookmakers
    timestamp: Optional[str] = None


class OddsAPIProvider:
    def __init__(self, config: Dict[str, Any]):
        # Leer la clave usando 'key' (como está en config.yaml + .env)
        self.api_key = config.get("key", config.get("api_key"))
        if not self.api_key:
            raise ValueError("No se encontró 'key' ni 'api_key' en la configuración de odds_api")
        self.base_url = config.get("base_url", "https://api.the-odds-api.com/v4")
        self.sports = config.get("sports", [
            "soccer_spain_la_liga",
            "soccer_england_premier_league",
            "soccer_uefa_champions_league",
            "tennis_atp",
            "basketball_nba",
        ])
        self.regions = config.get("regions", "eu")
        self.markets = config.get("markets", "h2h,totals,spreads")
        self.bookmakers = config.get("bookmakers", None)  # None -> todos los disponibles

    def get_events(self) -> List[AggregatedEvent]:
        aggregated_events = []
        for sport in self.sports:
            try:
                sport_events = self._fetch_sport(sport)
                aggregated_events.extend(sport_events)
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

        aggregated_events = []
        for game in data:
            event = self._parse_game(sport, game)
            if event:
                aggregated_events.append(event)
        return aggregated_events

    def _parse_game(self, sport: str, game: dict) -> Optional[AggregatedEvent]:
        try:
            event_name = f"{game['home_team']} vs {game['away_team']}"
            bookmakers_data = game.get("bookmakers", [])
            outcomes_by_market = {}  # market_name -> list of Outcome

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

            # Devolvemos un AggregatedEvent por cada mercado disponible
            aggregated_events = []
            for market_key, outcomes_list in outcomes_by_market.items():
                aggregated_events.append(
                    AggregatedEvent(
                        event_name=event_name,
                        sport=sport,
                        market=market_key,
                        outcomes=outcomes_list,
                        timestamp=game.get("commence_time")
                    )
                )
            # Si hay al menos un mercado, devolvemos la lista (pueden ser varios)
            # Pero nuestro pipeline espera un evento por mercado, así que retornamos todos.
            # Como get_events aplana la lista, devolvemos múltiples.
            return aggregated_events  # ahora retorna lista

        except Exception as e:
            logger.warning("Error parseando juego: %s", e)
        return None