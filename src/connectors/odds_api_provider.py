"""
Conector para The Odds API (the-odds-api.com)
Proporciona cuotas de múltiples bookmakers, incluyendo Pinnacle.
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from collections import namedtuple
import requests

from src.connectors.base import IDataProvider
from src.domain.entities import Snapshot, Market, MarketType

logger = logging.getLogger(__name__)

Selection = namedtuple("Selection", ["name", "odds"])

SPORT_MAP = {
    "soccer": "Football",
    "tennis": "Tennis",
    "basketball": "Basketball",
}

# Mapeo API -> (valor del MarketType) en lugar de atributo
# Así no dependemos del nombre exacto del miembro (ONE_X_TWO, MATCH_ODDS, etc.)
MARKET_TYPE_VALUE_MAP = {
    "h2h": {
        "soccer": "1X2",
        "tennis": "Tennis Winner",
        "basketball": "Basketball Moneyline",
    },
    "totals": {
        "soccer": "Over/Under 2.5",
        "tennis": "Total Games",
        "basketball": "Total Points",
    },
    "spreads": {
        "soccer": "Asian Handicap",
        "tennis": "Set Handicap",
        "basketball": "Point Spread",
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

    def _get_market_type(self, market_key: str, sport_key: str) -> Optional[MarketType]:
        """Obtiene el MarketType a partir del valor del enum."""
        value_map = MARKET_TYPE_VALUE_MAP.get(market_key)
        if not value_map:
            return None
        value = value_map.get(sport_key)
        if not value:
            return None
        try:
            return MarketType(value)      # Busca por valor
        except ValueError:
            return None

    def fetch_snapshots(self, limit: Optional[int] = None) -> List[Snapshot]:
        snapshots = []
        for sport_key in self.sports:
            url = f"{self.base_url}/sports/{sport_key}/odds/"
            params = {
                "apiKey": self.api_key,
                "regions": self.regions,
                "markets": self.markets,
                "bookmakers": ",".join(self.bookmakers),
                "oddsFormat": "decimal",
            }
            try:
                response = self._session.get(url, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Odds API: obtained {len(data)} events for {sport_key}")
            except requests.RequestException as e:
                logger.error(f"Error fetching odds for {sport_key}: {e}")
                continue

            sport_name = SPORT_MAP.get(sport_key)
            if not sport_name:
                continue

            for event in data:
                home_team = event.get("home_team", "")
                away_team = event.get("away_team", "")
                commence_time = event.get("commence_time")
                event_id = event.get("id")

                for bookmaker in event.get("bookmakers", []):
                    bookmaker_key = bookmaker.get("key")
                    if bookmaker_key not in self.bookmakers:
                        continue

                    for market in bookmaker.get("markets", []):
                        market_key = market.get("key")
                        market_type = self._get_market_type(market_key, sport_key)
                        if not market_type:
                            continue

                        selections = []
                        outcomes = market.get("outcomes", [])
                        for outcome in outcomes:
                            name = outcome.get("name")
                            price = outcome.get("price")
                            point = outcome.get("point")

                            if market_key == "h2h":
                                if name == home_team:
                                    sel_name = "home"
                                elif name == away_team:
                                    sel_name = "away"
                                elif name == "Draw":
                                    sel_name = "draw"
                                else:
                                    sel_name = name.lower()
                            elif market_key == "totals":
                                if "Over" in name:
                                    sel_name = f"over_{point}"
                                elif "Under" in name:
                                    sel_name = f"under_{point}"
                                else:
                                    sel_name = name.lower().replace(" ", "_")
                            elif market_key == "spreads":
                                sel_name = name.lower().replace(" ", "_")
                            else:
                                sel_name = name.lower().replace(" ", "_")

                            selections.append(Selection(name=sel_name, odds=price))

                        market_obj = Market(
                            market_type=market_type,
                            selections=selections,
                            parameters={"point": outcomes[0].get("point") if outcomes else None}
                        )

                        snap = Snapshot(
                            sport=sport_name,
                            event_name=f"{home_team} vs {away_team}",
                            market=market_obj,
                            timestamp=datetime.now(timezone.utc),
                            source="oddsapi",
                            metadata={
                                "event_id": event_id,
                                "bookmaker": bookmaker_key,
                                "commence_time": commence_time,
                            }
                        )
                        snapshots.append(snap)

                        if limit and len(snapshots) >= limit:
                            return snapshots[:limit]

        return snapshots