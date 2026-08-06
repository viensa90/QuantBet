"""
Conector para The Odds API (the-odds-api.com)
Proporciona cuotas de múltiples bookmakers.
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import requests

from src.connectors.base import IDataProvider
from src.domain.entities import Snapshot

logger = logging.getLogger(__name__)

MARKET_TYPE_VALUES = {
    "h2h": {
        "soccer": "1X2",
        "tennis": "Tennis Winner",
        "basketball": "Basketball Moneyline",
    },
    "totals": {
        "soccer": "Over/Under",
        "tennis": "Tennis Total Games",
        "basketball": "Basketball Total Points",
    },
    "spreads": {
        "soccer": "Asian Handicap",
        "tennis": "Tennis Set Handicap",
        "basketball": "Basketball Spread",
    },
}

class OddsAPIProvider(IDataProvider):
    """Obtiene snapshots desde The Odds API."""

    def __init__(self, config: Dict[str, Any]):
        self.api_key = config["api_key"]
        self.sports = config.get("sports", ["soccer", "tennis", "basketball"])
        self.bookmakers = config.get("bookmakers", ["pinnacle"])
        self.regions = config.get("regions", "eu")
        self.markets = config.get("markets", "h2h,spreads,totals")
        self.base_url = config.get("base_url", "https://api.the-odds-api.com/v4")
        self._session = requests.Session()

    def get_provider_name(self) -> str:
        return "TheOddsAPI"

    def validate_config(self) -> bool:
        return bool(self.api_key and self.sports and self.bookmakers)

    def _translate_selection(self, market_key: str, name: str, home: str, away: str, point: Optional[float]) -> str:
        if market_key == "h2h":
            if name == home:
                return "home"
            elif name == away:
                return "away"
            elif name == "Draw":
                return "draw"
            else:
                return name.lower()
        elif market_key == "totals":
            if "Over" in name:
                return f"over_{point}"
            elif "Under" in name:
                return f"under_{point}"
            else:
                return name.lower().replace(" ", "_")
        elif market_key == "spreads":
            return name.lower().replace(" ", "_")
        else:
            return name.lower().replace(" ", "_")

    def fetch_snapshots(self, limit: Optional[int] = None) -> List[Snapshot]:
        all_snapshots = []
        for sport_key in self.sports:
            for bookmaker in self.bookmakers:
                logger.info("Requesting %s from %s", sport_key, bookmaker)
                url = f"{self.base_url}/sports/{sport_key}/odds/"
                params = {
                    "apiKey": self.api_key,
                    "regions": self.regions,
                    "markets": self.markets,
                    "bookmakers": bookmaker,
                    "oddsFormat": "decimal",
                }
                try:
                    response = self._session.get(url, params=params, timeout=15)
                    response.raise_for_status()
                    data = response.json()
                    logger.info("Got %d events for %s/%s", len(data), bookmaker, sport_key)
                except Exception as e:
                    logger.error("Error on %s/%s: %s", bookmaker, sport_key, e)
                    continue

                for event in data:
                    home_team = event.get("home_team", "")
                    away_team = event.get("away_team", "")
                    commence_time = event.get("commence_time")
                    event_id = event.get("id")

                    for bm in event.get("bookmakers", []):
                        if bm.get("key") != bookmaker:
                            continue
                        for market in bm.get("markets", []):
                            market_key = market.get("key")
                            market_type_str = MARKET_TYPE_VALUES.get(market_key, {}).get(sport_key)
                            if not market_type_str:
                                continue

                            odds_data = {}
                            for outcome in market.get("outcomes", []):
                                name = outcome.get("name")
                                price = outcome.get("price")
                                point = outcome.get("point")
                                sel_name = self._translate_selection(market_key, name, home_team, away_team, point)
                                odds_data[sel_name] = price

                            if not odds_data:
                                continue

                            snap = Snapshot(
                                event_id=event_id,
                                event_name=f"{home_team} vs {away_team}",
                                market_type=market_type_str,
                                bookmaker=bookmaker,
                                odds_data=odds_data,
                                timestamp=datetime.now(timezone.utc),
                                source="oddsapi",
                                metadata={"commence_time": commence_time, "sport_key": sport_key}
                            )
                            all_snapshots.append(snap)

        # Aplicar límite solo al final
        if limit and len(all_snapshots) > limit:
            return all_snapshots[:limit]
        return all_snapshots