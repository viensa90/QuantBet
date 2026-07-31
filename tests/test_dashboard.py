"""
Tests para el dashboard web.
"""

import pytest
from unittest.mock import Mock, patch
import json

from src.web.app import create_app


@pytest.fixture
def client():
    """Cliente de prueba para Flask."""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    """Test: Ruta principal carga correctamente."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'QuantBet Dashboard' in response.data


def test_api_status(client):
    """Test: API de estado retorna datos correctos."""
    response = client.get('/api/status')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'version' in data
    assert 'status' in data
    assert data['status'] == 'running'


def test_api_snapshots(client):
    """Test: API de snapshots retorna lista."""
    response = client.get('/api/snapshots')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert isinstance(data, list)


def test_api_opportunities(client):
    """Test: API de oportunidades retorna lista."""
    response = client.get('/api/opportunities')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert isinstance(data, list)


def test_api_event_detail_not_found(client):
    """Test: Evento no encontrado retorna 404."""
    response = client.get('/api/event/NO_EXISTE')
    assert response.status_code == 404