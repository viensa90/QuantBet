import time
from typing import List, Dict
import requests

from src.connectors.base import IDataProvider
from src.domain.entities import Outcome
from src.config_loader import ConfigLoader
from src.logger import log


class OddsAPIProvider(IDataProvider):
    BASE_URL = "https://api.the-odds-api.com/v4/sports"

    def __init__(self):
        cfg = ConfigLoader()
        self.api_key = cfg.odds_api_key
        if not self.api_key:
            raise ValueError("ODDS_API_KEY no configurada en .env")
        allowed = cfg['allowed_bookmakers'] if 'allowed_bookmakers' in cfg._config else []
        self.allowed_bookmakers = {b.lower() for b in allowed}
        self.session = requests.Session()
        self.session.headers.update({"accept": "application/json"})

    def fetch(self, sport_key: str, regions: str = "us,eu,uk", markets: str = "h2h") -> List[Outcome]:
        params = {
            "apiKey": self.api_key,
            "regions": regions,
            "markets": markets,
            "oddsFormat": "decimal",
        }
        url = f"{self.BASE_URL}/{sport_key}/odds"
        outcomes = []
        try:
            resp = self._request_with_retry(url, params)
            data = resp.json()
            for game in data:
                outcomes.extend(self._parse_game(game, sport_key))
            log.info(f"Obtenidos {len(outcomes)} outcomes de {sport_key}")
            return outcomes
        except Exception as e:
            log.error(f"Error al obtener cuotas de {sport_key}: {e}")
            return []

    def _request_with_retry(self, url, params, retries=3, backoff=2, timeout=10):
        for attempt in range(retries):
            try:
                resp = self.session.get(url, params=params, timeout=timeout)
                resp.raise_for_status()
                remaining = resp.headers.get("x-requests-remaining", "?")
                log.info(f"Créditos restantes The Odds API: {remaining}")
                return resp
            except requests.exceptions.RequestException as e:
                if hasattr(e, 'response') and e.response is not None:
                    log.warning(f"Intento {attempt+1} fallido: HTTP {e.response.status_code}")
                else:
                    log.warning(f"Intento {attempt+1} fallido: {type(e).__name__}")
                if attempt < retries - 1:
                    time.sleep(backoff * (attempt + 1))
                else:
                    raise

    def _parse_game(self, game: Dict, sport_key: str) -> List[Outcome]:
        outcomes = []
        event_name = f"{game.get('home_team')} vs {game.get('away_team')}"
        bookmakers_data = game.get("bookmakers", [])

        for bk in bookmakers_data:
            bookmaker = bk.get("key")
            if bookmaker.lower() not in self.allowed_bookmakers:
                continue

            markets_list = bk.get("markets", [])
            for mkt in markets_list:
                market_key = mkt.get("key")
                if "_lay" in market_key:
                    continue

                point = None
                if market_key == "totals":
                    point = mkt.get("point")

                for out in mkt.get("outcomes", []):
                    name = out.get("name")
                    price = out.get("price")
                    point_outcome = out.get("point", None)
                    final_point = point_outcome if point_outcome is not None else point

                    outcomes.append(Outcome(
                        bookmaker=bookmaker,
                        sport=sport_key,
                        event_name=event_name,
                        market=market_key,
                        name=name,
                        price=price,
                        point=final_point,
                        timestamp=time.time()
                    ))
        return outcomes