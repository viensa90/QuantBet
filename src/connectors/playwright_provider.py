"""Conector web: scraping con Playwright."""
from typing import List
from playwright.sync_api import sync_playwright
from src.connectors.base import IDataProvider
from src.domain.entities import Snapshot
from src.config_loader import config

class PlaywrightProvider(IDataProvider):
    """Obtiene snapshots mediante scraping web con Playwright."""

    def __init__(self):
        self.sites = config.get('connectors.playwright.sites', [])

    def get_snapshots(self) -> List[Snapshot]:
        snapshots = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for site in self.sites:
                try:
                    page = browser.new_page()
                    page.goto(site['url'], timeout=15000)
                    html = page.content()
                    page.close()
                    parsed = _parse_html(html, site)
                    snapshots.extend(parsed)
                except Exception as e:
                    from src.logger import logger
                    logger.error(f"Error scraping {site['name']}: {e}")
            browser.close()
        return snapshots

def _parse_html(html: str, site: dict) -> List[Snapshot]:
    """Parsea el HTML y extrae snapshots según los selectores configurados."""
    from bs4 import BeautifulSoup
    from datetime import datetime
    import uuid

    soup = BeautifulSoup(html, 'html.parser')
    snapshots = []
    rows = soup.select(site.get('row_selector', 'tr'))
    for row in rows:
        try:
            event_name = row.select_one(site['event_selector']).get_text(strip=True)
            market = site.get('market', '1X2')
            # Las cuotas pueden ser múltiples (local, empate, visitante)
            odds_elements = row.select(site['odds_selector'])
            for i, odd_el in enumerate(odds_elements, start=1):
                odd_text = odd_el.get_text(strip=True)
                try:
                    odd_value = float(odd_text)
                except ValueError:
                    continue
                outcome = site.get('outcomes', ['1', 'X', '2'])[i-1] if i <= 3 else f"outcome_{i}"
                snapshot = Snapshot(
                    snapshot_id=str(uuid.uuid4()),
                    provider='playwright',
                    event_name=event_name,
                    market=market,
                    outcome=outcome,
                    odds=odd_value,
                    timestamp=datetime.utcnow().isoformat()
                )
                snapshots.append(snapshot)
        except Exception:
            continue
    return snapshots