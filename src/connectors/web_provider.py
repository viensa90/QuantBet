"""
Conector web con Playwright para scraping de casas de apuestas.
Implementa IDataProvider para obtener cuotas en tiempo real.
"""

import time
import re
from typing import List, Dict, Optional, Any
from datetime import datetime
from decimal import Decimal

from playwright.sync_api import sync_playwright, Browser, Page

from src.domain.entities import Snapshot, MarketType
from src.connectors.base import IDataProvider
from src.logger import get_logger

logger = get_logger(__name__)


class WebProvider(IDataProvider):
    """Proveedor de datos vía web scraping con Playwright."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el proveedor web.
        
        Args:
            config: Configuración de web_scraping desde config.yaml
        """
        self.config = config
        self.bookmakers = config.get('bookmakers', {})
        self.headless = config.get('headless', True)
        self.timeout = config.get('timeout', 30000)
        self._browser: Optional[Browser] = None
        self._playwright = None
        
    def _get_browser(self) -> Browser:
        """Obtiene o crea instancia del navegador (lazy loading)."""
        if self._browser is None:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
                headless=self.headless
            )
            logger.info("Navegador iniciado (headless=%s)", self.headless)
        return self._browser
    
    def _extract_odds_from_page(self, page: Page, selectors: Dict[str, str]) -> Dict[str, Decimal]:
        """
        Extrae cuotas de una página usando selectores CSS.
        
        Args:
            page: Página de Playwright
            selectors: Diccionario {mercado: selector_css}
            
        Returns:
            Diccionario {mercado: cuota}
        """
        odds = {}
        
        for market, selector in selectors.items():
            try:
                # Esperar a que el elemento exista
                element = page.locator(selector).first
                if element.count() > 0:
                    text = element.text_content().strip()
                    # Limpiar y convertir a Decimal
                    clean_text = re.sub(r'[^\d.]', '', text)
                    if clean_text:
                        odds[market] = Decimal(clean_text)
                        logger.debug("Cuota extraída: %s = %s", market, clean_text)
            except Exception as e:
                logger.warning("Error extrayendo %s con selector %s: %s", 
                             market, selector, str(e))
                
        return odds
    
    def _scrape_bookmaker(self, bookmaker_name: str, config: Dict) -> List[Dict]:
        """
        Scrapea un bookmaker específico.
        
        Args:
            bookmaker_name: Nombre del bookmaker
            config: Configuración del bookmaker (url, selectors, events)
            
        Returns:
            Lista de snapshots en bruto
        """
        url = config.get('url')
        selectors = config.get('selectors', {})
        events_to_scrape = config.get('events', [])
        
        if not url or not selectors:
            logger.warning("Configuración incompleta para %s", bookmaker_name)
            return []
        
        logger.info("Scrapeando %s desde %s", bookmaker_name, url)
        
        browser = self._get_browser()
        page = browser.new_page()
        
        snapshots = []
        
        try:
            # Navegar a la URL
            page.goto(url, timeout=self.timeout)
            page.wait_for_load_state('networkidle')
            
            # Si hay eventos específicos, navegar a cada uno
            if events_to_scrape:
                for event in events_to_scrape:
                    event_url = event.get('url')
                    event_name = event.get('name', 'Unknown')
                    
                    if event_url:
                        logger.info("Navegando a evento: %s", event_name)
                        page.goto(event_url, timeout=self.timeout)
                        page.wait_for_load_state('networkidle')
                    
                    # Extraer cuotas
                    odds = self._extract_odds_from_page(page, selectors)
                    
                    if odds:
                        snapshots.append({
                            'source': bookmaker_name,
                            'event_id': event.get('id', f"{bookmaker_name}_{int(time.time())}"),
                            'event_name': event_name,
                            'timestamp': datetime.now().isoformat(),
                            'odds': odds,
                            'market_type': event.get('market_type', '1X2')
                        })
            else:
                # Si no hay eventos específicos, extraer todo de la página principal
                odds = self._extract_odds_from_page(page, selectors)
                if odds:
                    snapshots.append({
                        'source': bookmaker_name,
                        'event_id': f"{bookmaker_name}_{int(time.time())}",
                        'event_name': f"Evento {bookmaker_name}",
                        'timestamp': datetime.now().isoformat(),
                        'odds': odds,
                        'market_type': '1X2'
                    })
                    
        except Exception as e:
            logger.error("Error scrapeando %s: %s", bookmaker_name, str(e))
        finally:
            page.close()
            
        return snapshots
    
    def fetch_snapshots(self, event_id: Optional[str] = None) -> List[Snapshot]:
        """
        Obtiene snapshots de todos los bookmakers configurados.
        
        Args:
            event_id: ID del evento específico (opcional)
            
        Returns:
            Lista de Snapshots
        """
        all_snapshots = []
        
        for bookmaker_name, config in self.bookmakers.items():
            # Si se especifica event_id, filtrar
            if event_id:
                # Verificar si el evento existe en la configuración
                event_exists = any(
                    e.get('id') == event_id 
                    for e in config.get('events', [])
                )
                if not event_exists:
                    continue
            
            raw_snapshots = self._scrape_bookmaker(bookmaker_name, config)
            
            for raw in raw_snapshots:
                try:
                    # Construir Snapshot
                    snapshot = Snapshot(
                        event_id=raw['event_id'],
                        event_name=raw['event_name'],
                        source=raw['source'],
                        timestamp=datetime.fromisoformat(raw['timestamp']),
                        odds=raw['odds'],
                        market_type=MarketType(raw.get('market_type', '1X2'))
                    )
                    all_snapshots.append(snapshot)
                except Exception as e:
                    logger.error("Error construyendo snapshot: %s", str(e))
        
        logger.info("Obtenidos %d snapshots de %d bookmakers", 
                   len(all_snapshots), len(self.bookmakers))
        
        return all_snapshots
    
    def close(self):
        """Cierra el navegador y libera recursos."""
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
        logger.info("Recursos del navegador liberados")
    
    def __enter__(self):
        """Context manager enter."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()