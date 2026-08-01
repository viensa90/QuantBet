"""
Tests para documentación Swagger/OpenAPI
Versión: 0.3.2
"""

import json
import pytest
from src.web.app import create_app


@pytest.fixture
def client():
    """Cliente de pruebas Flask"""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_swagger_ui_accessible(client):
    """Test: La interfaz Swagger UI es accesible"""
    response = client.get('/swagger/')
    assert response.status_code == 200
    assert b'Swagger UI' in response.data or b'QuantBet API' in response.data


def test_swagger_json_valid(client):
    """Test: El archivo OpenAPI JSON es válido"""
    response = client.get('/api/v1/swagger.json')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['swagger'] == '2.0'
    assert data['info']['title'] == 'QuantBet API'
    assert 'paths' in data
    assert '/metrics' in data['paths'] or '/api/v1/metrics' in data['paths']


def test_swagger_endpoints_match_api(client):
    """Test: Los endpoints documentados coinciden con la API real"""
    # Obtener Swagger
    swagger_response = client.get('/api/v1/swagger.json')
    swagger_data = json.loads(swagger_response.data)
    
    # Verificar endpoints críticos
    endpoints = list(swagger_data['paths'].keys())
    
    # Verificar que los endpoints reales existen
    for endpoint in ['/metrics', '/markets', '/opportunities', '/snapshots']:
        # Buscar con o sin prefijo /api/v1
        found = any(endpoint in e or endpoint.replace('/api/v1', '') in e for e in endpoints)
        assert found, f"Endpoint {endpoint} no encontrado en Swagger"


def test_swagger_has_models(client):
    """Test: Swagger define modelos de datos"""
    response = client.get('/api/v1/swagger.json')
    data = json.loads(response.data)
    
    assert 'definitions' in data
    assert 'Opportunity' in data['definitions']
    opp_def = data['definitions']['Opportunity']
    assert 'event' in opp_def['properties']
    assert 'strategy' in opp_def['properties']
    assert 'profit_percent' in opp_def['properties']


def test_api_metrics_returns_correct_format(client):
    """Test: El endpoint /metrics devuelve el formato correcto"""
    response = client.get('/api/v1/metrics')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'total_opportunities' in data
    assert 'active_markets' in data
    assert 'strategies' in data
    assert 'arbitrage' in data['strategies']
    assert 'last_update' in data