"""
Conector para The Odds API.
- Filtra por bookmakers (lista blanca).
- Timeout 10s y reintentos automáticos (3 intentos con backoff).
- Ignora mercados _lay.
- Incluye campo 'point' para líneas exactas (totals).
"""
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List, Optional
from src.connectors.base import BaseProvider, AggregatedEvent, Outcome
from src.logger import logger

class OddsAPIProvider(BaseProvider):
    def __init__(self, api_key: str, bookmakers: Optional[str] = None,
                 regions: str = "eu", markets: str = "h2h,totals"):
        self.api_key = api_key
        self.bookmakers = bookmakers  # ej: "Pinnacle,1xBet,BetOnline.ag"
        self.regions = regions
        self.markets = markets
        self.base_url = "https://api.the-odds-api.com/v4"

    def fetch_events(self, sport: str) -> List[AggregatedEvent]:
        """Obtiene eventos para un deporte, filtrando por bookmakers."""
        return self._fetch_sport(sport)

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

        logger.info("Consultando Odds API: %s (bookmakers: %s)", url, self.bookmakers)

        # --- Session con reintentos y timeout ---
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        session.mount('https://', HTTPAdapter(max_retries=retries))

        try:
            resp = session.get(url, params=params, timeout=10)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error("Error al consultar Odds API: %s", e)
            return []

        data = resp.json()
        events = []
        for game in data:
            parsed = self._parse_game(sport, game)
            if parsed:
                events.extend(parsed)
        return events

    def _parse_game(self, sport: str, game: dict) -> List[AggregatedEvent]:
        """
        Parsea un partido y devuelve una lista de AggregatedEvent (uno por mercado).
        - Ignora mercados que contengan '_lay'.
        - Cada outcome incluye el campo 'point' (línea exacta para totals).
        """
        events = []
        home = game.get("home_team", "Unknown")
        away = game.get("away_team", "Unknown")
        event_name = f"{home} vs {away}"
        commence_time = game.get("commence_time", "")

        for bookmaker in game.get("bookmakers", []):
            bk_name = bookmaker.get("key", "unknown")
            # Si definimos bookmakers en la petición, la API ya filtra,
            # pero lo dejamos por si acaso.
            if self.bookmakers and bk_name not in [b.strip() for b in self.bookmakers.split(",")]:
                continue

            for market in bookmaker.get("markets", []):
                market_key = market.get("key", "")
                # Ignoramos mercados _lay (solo queremos back)
                if "_lay" in market_key:
                    continue

                outcomes = []
                for outcome in market.get("outcomes", []):
                    name = outcome.get("name", "")
                    price = outcome.get("price", 0.0)
                    point = outcome.get("point", None)  # línea exacta para totals
                    outcomes.append(Outcome(
                        bookmaker=bk_name,
                        name=name,
                        price=price,
                        point=point,
                        market=market_key
                    ))

                if outcomes:
                    events.append(AggregatedEvent(
                        sport=sport,
                        event_name=event_name,
                        commence_time=commence_time,
                        market=market_key,
                        outcomes=outcomes,
                        details={
                            "home": home,
                            "away": away,
                            "bookmaker": bk_name,
                            "point": outcomes[0].point if outcomes else None
                        }
                    ))
        return events