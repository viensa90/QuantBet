"""
Proveedor de datos: The Odds API (v4)
"""
import requests
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from time import sleep
from datetime import datetime, timezone
from src.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Outcome:
    bookmaker: str
    name: str
    price: float
    point: Optional[float] = None


@dataclass
class AggregatedEvent:
    event_name: str
    sport: str
    market: str
    outcomes: List[Outcome]
    timestamp: Optional[str] = None
    is_live: bool = False
    match_time: Optional[str] = None


class OddsAPIProvider:
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get("key") or config.get("api_key")
        if not self.api_key:
            raise ValueError("No se encontró 'key' ni 'api_key' en la configuración de odds_api")
        self.base_url = config.get("base_url", "https://api.the-odds-api.com/v4")
        self.sports = config.get("sports", ["soccer_spain_la_liga", "soccer_epl"])
        self.regions = config.get("regions", "eu")
        self.markets = config.get("markets", "h2h,totals")
        self.bookmakers_param = config.get("bookmakers", None)
        self.allowed_bookmakers = [b.lower() for b in config.get("allowed_bookmakers", [])]
        self.timeout = config.get("timeout", 10)
        self.max_retries = config.get("max_retries", 3)
        self.exclude_live = config.get("exclude_live", False)
        self.min_minutes_to_start = config.get("min_minutes_to_start", 0)

    def get_events(self) -> List[AggregatedEvent]:
        aggregated_events = []
        now = datetime.now(timezone.utc)
        for sport in self.sports:
            try:
                sport_events = self._fetch_sport(sport)
                if self.exclude_live:
                    sport_events = [
                        e for e in sport_events
                        if e.timestamp and self._is_future(e.timestamp, now)
                    ]
                    logger.info("Eventos después de filtrar en vivo: %d", len(sport_events))
                aggregated_events.extend(sport_events)
            except Exception as e:
                logger.error("Error obteniendo eventos para %s: %s", sport, e)
        return aggregated_events

    def _is_future(self, commence_time_str: str, now: datetime) -> bool:
        try:
            event_time = datetime.fromisoformat(commence_time_str.replace("Z", "+00:00"))
            margin = self.min_minutes_to_start * 60
            return (event_time - now).total_seconds() > margin
        except:
            return True

    def _fetch_sport(self, sport: str) -> List[AggregatedEvent]:
        url = f"{self.base_url}/sports/{sport}/odds"
        params = {
            "apiKey": self.api_key,
            "regions": self.regions,
            "markets": self.markets,
            "dateFormat": "iso",
            "oddsFormat": "decimal",
        }
        if self.bookmakers_param:
            params["bookmakers"] = self.bookmakers_param

        last_exception = None
        for attempt in range(self.max_retries):
            try:
                logger.info("Consultando Odds API: %s (intento %d)", url, attempt+1)
                resp = requests.get(url, params=params, timeout=self.timeout)
                resp.raise_for_status()
                data = resp.json()
                events = []
                for game in data:
                    parsed = self._parse_game(sport, game)
                    if parsed:
                        events.extend(parsed)
                return events
            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.warning("Intento %d fallido: %s", attempt+1, e)
                sleep(2 ** attempt)
        raise last_exception

    def _parse_game(self, sport: str, game: dict) -> Optional[List[AggregatedEvent]]:
        try:
            event_name = f"{game['home_team']} vs {game['away_team']}"
            bookmakers_data = game.get("bookmakers", [])
            grouped = {}

            for bk in bookmakers_data:
                bookmaker_name = bk["title"]
                if self.allowed_bookmakers and bookmaker_name.lower() not in self.allowed_bookmakers:
                    continue
                for market in bk.get("markets", []):
                    market_key = market["key"]
                    if "_lay" in market_key:
                        continue
                    for oc in market.get("outcomes", []):
                        point = oc.get("point")
                        key = (market_key, point)
                        grouped.setdefault(key, [])
                        grouped[key].append(
                            Outcome(
                                bookmaker=bookmaker_name,
                                name=oc["name"],
                                price=oc["price"],
                                point=point
                            )
                        )

            # Determinar si está en vivo comparando la hora de inicio con ahora
            commence_time = game.get("commence_time")
            is_live = False
            if commence_time:
                try:
                    event_time = datetime.fromisoformat(commence_time.replace("Z", "+00:00"))
                    now = datetime.now(timezone.utc)
                    is_live = event_time < now
                except:
                    pass

            aggregated = []
            for (market_key, point), outcomes_list in grouped.items():
                market_name = market_key
                if point is not None:
                    market_name = f"{market_key} {point}"
                aggregated.append(
                    AggregatedEvent(
                        event_name=event_name,
                        sport=sport,
                        market=market_name,
                        outcomes=outcomes_list,
                        timestamp=commence_time,
                        is_live=is_live,
                        match_time=None
                    )
                )
            return aggregated
        except Exception as e:
            logger.warning("Error parseando juego: %s", e)
            return None