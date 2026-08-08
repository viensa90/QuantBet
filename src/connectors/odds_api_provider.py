"""
Proveedor de datos: The Odds API (v4)
Documentación: https://the-odds-api.com/liveapi/guides/v4/
"""
import requests
from typing import List, Optional, Dict, Any
from src.connectors.base import IDataProvider
from src.domain.entities import Snapshot, Odds
from src.logger import get_logger

logger = get_logger(__name__)

class OddsAPIProvider(IDataProvider):
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

    def get_events(self) -> List[Snapshot]:
        snapshots = []
        for sport in self.sports:
            try:
                sport_snapshots = self._fetch_sport(sport)
                snapshots.extend(sport_snapshots)
            except Exception as e:
                logger.error("Error obteniendo eventos para %s: %s", sport, e)
        return snapshots

    def _fetch_sport(self, sport: str) -> List[Snapshot]:
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

        snapshots = []
        for game in data:
            snap = self._parse_game(sport, game)
            if snap:
                snapshots.append(snap)
        return snapshots

    def _parse_game(self, sport: str, game: dict) -> Optional[Snapshot]:
        try:
            event_name = f"{game['home_team']} vs {game['away_team']}"
            bookmakers_data = game.get("bookmakers", [])
            outcomes = []
            for bk in bookmakers_data:
                bookmaker_name = bk["title"]
                for market in bk.get("markets", []):
                    market_name = market["key"]
                    for oc in market.get("outcomes", []):
                        outcomes.append(Odds(
                            bookmaker=bookmaker_name,
                            name=oc["name"],
                            price=oc["price"],
                            market=market_name,
                            timestamp=game.get("commence_time")
                        ))
            if outcomes:
                # Determinamos el mercado mayoritario (simplificado: el del primer outcome)
                market = outcomes[0].market
                return Snapshot(
                    event_name=event_name,
                    sport=sport,
                    market=market,
                    outcomes=outcomes,
                    timestamp=game.get("commence_time")
                )
        except Exception as e:
            logger.warning("Error parseando juego: %s", e)
        return None