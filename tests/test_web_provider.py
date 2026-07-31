"""
Tests para el conector web con Playwright.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import datetime

from src.connectors.web_provider import WebProvider
from src.domain.entities import Snapshot, MarketType


@pytest.fixture
def web_config():
    return {
        "headless": True,
        "timeout": 10000,
        "bookmakers": {
            "test_bookmaker": {
                "url": "https://test.com",
                "selectors": {
                    "Local": ".home-odds",
                    "Empate": ".draw-odds",
                    "Visitante": ".away-odds"
                },
                "events": [
                    {
                        "id": "EVT-001",
                        "name": "Test Event",
                        "url": "https://test.com/event/1",
                        "market_type": "1X2"
                    }
                ]
            }
        }
    }


@patch('src.connectors.web_provider.sync_playwright')
def test_fetch_snapshots_success(mock_playwright, web_config):
    """Test: Obtener snapshots correctamente desde web."""
    
    # Mock de Playwright
    mock_page = Mock()
    mock_locator = Mock()
    mock_locator.first.count.return_value = 1
    mock_locator.first.text_content.return_value = "2.10"
    mock_page.locator.return_value = mock_locator
    
    mock_browser = Mock()
    mock_browser.new_page.return_value = mock_page
    
    mock_playwright_instance = Mock()
    mock_playwright_instance.chromium.launch.return_value = mock_browser
    mock_playwright.return_value.__enter__.return_value = mock_playwright_instance
    mock_playwright.return_value.__exit__.return_value = None
    
    # Crear provider
    provider = WebProvider(web_config)
    
    # Ejecutar
    snapshots = provider.fetch_snapshots()
    
    # Verificar
    assert len(snapshots) == 1
    assert snapshots[0].event_id == "EVT-001"
    assert snapshots[0].source == "test_bookmaker"
    assert snapshots[0].odds["Local"] == Decimal("2.10")
    assert snapshots[0].market_type == MarketType.MERCADO_1X2
    
    provider.close()


def test_extract_odds_from_page(web_config):
    """Test: Extraer cuotas de una página mockeada."""
    provider = WebProvider(web_config)
    
    mock_page = Mock()
    mock_locator = Mock()
    mock_locator.first.count.return_value = 1
    mock_locator.first.text_content.return_value = "1.85"
    mock_page.locator.return_value = mock_locator
    
    odds = provider._extract_odds_from_page(
        mock_page,
        {"Local": ".home-odds"}
    )
    
    assert odds["Local"] == Decimal("1.85")


def test_extract_odds_from_page_no_element(web_config):
    """Test: Si no hay elemento, retorna vacío."""
    provider = WebProvider(web_config)
    
    mock_page = Mock()
    mock_locator = Mock()
    mock_locator.first.count.return_value = 0
    mock_page.locator.return_value = mock_locator
    
    odds = provider._extract_odds_from_page(
        mock_page,
        {"Local": ".home-odds"}
    )
    
    assert odds == {}


def test_close_browser(web_config):
    """Test: Cerrar navegador libera recursos."""
    provider = WebProvider(web_config)
    
    # Simular que el navegador está abierto
    mock_browser = Mock()
    mock_playwright = Mock()
    provider._browser = mock_browser
    provider._playwright = mock_playwright
    
    provider.close()
    
    mock_browser.close.assert_called_once()
    mock_playwright.stop.assert_called_once()
    assert provider._browser is None
    assert provider._playwright is None


def test_context_manager(web_config):
    """Test: Context manager cierra recursos."""
    with WebProvider(web_config) as provider:
        assert provider._browser is None  # Lazy loading, aún no iniciado
        # Simular uso...
        
    # Al salir del context, se cierra
    # No podemos verificar directamente porque el navegador no se inició,
    # pero verificamos que no hay error
    assert True