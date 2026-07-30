import pytest
from unittest.mock import patch, MagicMock
from src.connectors.playwright_provider import _parse_html, PlaywrightProvider
from src.domain.entities import Snapshot

# HTML simulado de dos eventos
SAMPLE_HTML = """
<html><body>
<table>
  <tr>
    <td class="event">Manchester vs Liverpool</td>
    <td class="odds">2.50</td>
    <td class="odds">3.10</td>
    <td class="odds">2.90</td>
  </tr>
  <tr>
    <td class="event">Barcelona vs Madrid</td>
    <td class="odds">1.80</td>
    <td class="odds">3.50</td>
    <td class="odds">4.00</td>
  </tr>
</table>
</body></html>
"""

SITE_CONFIG = {
    'name': 'test_site',
    'row_selector': 'tr',
    'event_selector': '.event',
    'odds_selector': '.odds',
    'outcomes': ['1', 'X', '2']
}

def test_parse_html_returns_snapshots():
    snapshots = _parse_html(SAMPLE_HTML, SITE_CONFIG)
    assert len(snapshots) == 6  # 2 eventos * 3 cuotas
    assert all(isinstance(s, Snapshot) for s in snapshots)

def test_snapshot_structure():
    snapshots = _parse_html(SAMPLE_HTML, SITE_CONFIG)
    first = snapshots[0]
    assert first.provider == 'playwright'
    assert first.event_name == 'Manchester vs Liverpool'
    assert first.market == '1X2'
    assert first.outcome == '1'
    assert first.odds == 2.50
    assert first.snapshot_id is not None
    assert first.timestamp is not None

def test_invalid_odds_ignored():
    html = '<tr><td class="event">Test</td><td class="odds">N/A</td></tr>'
    snapshots = _parse_html(html, SITE_CONFIG)
    assert len(snapshots) == 0

@patch('src.connectors.playwright_provider.sync_playwright')
def test_provider_integration_mocked(mock_playwright):
    # Simular la página que devuelve nuestro HTML de prueba
    mock_page = MagicMock()
    mock_page.content.return_value = SAMPLE_HTML
    mock_browser = MagicMock()
    mock_browser.new_page.return_value = mock_page
    mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser

    provider = PlaywrightProvider()
    provider.sites = [SITE_CONFIG]  # forzamos la config para el test
    snapshots = provider.get_snapshots()
    assert len(snapshots) == 6

@patch('src.connectors.playwright_provider.sync_playwright')
def test_provider_handles_scraping_error(mock_playwright, caplog):
    mock_page = MagicMock()
    mock_page.goto.side_effect = Exception('Timeout')
    mock_browser = MagicMock()
    mock_browser.new_page.return_value = mock_page
    mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser

    provider = PlaywrightProvider()
    provider.sites = [SITE_CONFIG]
    snapshots = provider.get_snapshots()
    assert len(snapshots) == 0
    assert 'Error scraping' in caplog.text