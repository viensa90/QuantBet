# tests/test_integration.py
"""
Tests de integración para el MVP de QuantBet.
Verifica el pipeline completo: CSV → Motor → Scorer → DB
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.connectors import CSVProvider
from src.core.arbitrage import ArbitrageEngine
from src.core.scorer import OpportunityScorer
from src.storage import DatabaseManager, Repository
from src.domain.entities import Snapshot


class TestIntegration:
    """Tests de integración del pipeline completo."""
    
    @pytest.fixture
    def provider(self):
        """Fixture: Proveedor CSV con datos de prueba."""
        return CSVProvider()
    
    @pytest.fixture
    def engine(self):
        """Fixture: Motor de arbitraje."""
        return ArbitrageEngine()
    
    @pytest.fixture
    def scorer(self):
        """Fixture: Puntuador de oportunidades."""
        return OpportunityScorer()
    
    @pytest.fixture
    def db(self):
        """Fixture: Base de datos para tests."""
        db = DatabaseManager()
        yield db
        # Limpieza: no eliminamos la DB para mantener auditoría
    
    def test_full_pipeline_arbitrage(self, provider, engine, scorer):
        """Test: Pipeline completo detecta surebet en EVT-003."""
        # 1. Obtener snapshots
        snapshots = provider.fetch_snapshots(event_id="EVT-003")
        assert len(snapshots) == 3
        
        # 2. Detectar arbitraje
        opportunities = engine.detect_arbitrage(snapshots)
        assert len(opportunities) == 1
        
        # 3. Puntuar oportunidad
        scored = scorer.score_opportunity(opportunities[0])
        assert scored.opportunity_score > 0
        assert scored.expected_return > 0
        
        # 4. Verificar que es ejecutable
        assert scored.opportunity_score >= 60.0, \
            f"Surebet debería tener score alto, obtuvo: {scored.opportunity_score}"
    
    def test_full_pipeline_no_arbitrage(self, provider, engine):
        """Test: Pipeline completo no detecta falsos positivos en EVT-001."""
        snapshots = provider.fetch_snapshots(event_id="EVT-001")
        assert len(snapshots) == 9  # 3 bookmakers × 3 outcomes
        
        opportunities = engine.detect_arbitrage(snapshots)
        assert len(opportunities) == 0, \
            "EVT-001 no debería tener arbitraje"
    
    def test_csv_provider_events(self, provider):
        """Test: CSV Provider lista eventos correctamente."""
        events = provider.get_available_events()
        assert len(events) == 3
        assert "EVT-001" in events
        assert "EVT-002" in events
        assert "EVT-003" in events
    
    def test_snapshot_persistence(self, provider, db):
        """Test: Snapshots se persisten correctamente."""
        repo = Repository(db)
        snapshots = provider.fetch_snapshots(event_id="EVT-003")
        
        for snap in snapshots:
            # No debería lanzar excepción
            repo.save_snapshot(snap)
        
        # Verificar que se guardaron
        # Nota: Como los snapshots son inmutables, si intentamos
        # guardarlos dos veces debería fallar (UNIQUE constraint)
        with pytest.raises(Exception):
            repo.save_snapshot(snapshots[0])
    
    def test_end_to_end_decision(self, provider, engine, scorer):
        """Test: Flujo completo desde datos hasta decisión."""
        # Pipeline completo para EVT-003
        snapshots = provider.fetch_snapshots(event_id="EVT-003")
        opportunities = engine.detect_arbitrage(snapshots)
        
        assert len(opportunities) == 1
        
        scored = scorer.score_opportunity(opportunities[0])
        
        # Verificar estructura de la oportunidad
        assert hasattr(scored, 'event_id')
        assert hasattr(scored, 'expected_return')
        assert hasattr(scored, 'best_odds')
        assert hasattr(scored, 'opportunity_score')
        
        # Verificar que es una surebet real
        overround = sum(1/odd for odd in scored.best_odds.values())
        assert overround < 1.0, \
            f"Overround debe ser < 1.0 para surebet, es: {overround}"
    
    def test_multiple_events_analysis(self, provider, engine):
        """Test: Análisis de múltiples eventos."""
        all_snapshots = provider.fetch_snapshots()
        assert len(all_snapshots) == 21
        
        # Agrupar por evento
        events = {}
        for snap in all_snapshots:
            events.setdefault(snap.event_id, []).append(snap)
        
        # Solo EVT-003 debe tener arbitraje
        for evt_id, evt_snapshots in events.items():
            opps = engine.detect_arbitrage(evt_snapshots)
            if evt_id == "EVT-003":
                assert len(opps) == 1, f"{evt_id} debería tener 1 arbitraje"
            else:
                assert len(opps) == 0, f"{evt_id} no debería tener arbitraje"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])