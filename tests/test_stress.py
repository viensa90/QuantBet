"""
tests/test_stress.py
Pruebas de estrés para QuantBet - 1000+ eventos
Versión: 0.3.1
"""

import pytest
import time
import random
import tempfile
from datetime import datetime, timedelta
from typing import List
from pathlib import Path

from src.domain.entities import Snapshot, Decision
from src.storage.database import Database
from src.storage.repository import Repository
from src.storage.migrations import apply_migrations
from src.core.arbitrage import ArbitrageEngine
from src.core.scorer import OpportunityScorer
from src.core.value_betting import ValueBetDetector
from src.core.dutching import DutchingCalculator
from src.core.probability_model import ProbabilityModelFactory

# Marcar tests como de estrés (pueden ser lentos)
pytestmark = pytest.mark.slow

class StressTestDataGenerator:
    """Generador de datos masivos para tests de estrés"""
    
    @staticmethod
    def generate_snapshots(count: int = 1000, 
                          market_types: List[str] = None) -> List[Snapshot]:
        """Genera N snapshots aleatorios"""
        if market_types is None:
            market_types = ['1X2', 'Over/Under', 'Asian Handicap', 'Double Chance']
        
        snapshots = []
        base_time = datetime.now()
        
        for i in range(count):
            # Datos aleatorios
            event_id = f"event_{i:05d}"
            event_name = f"Match {i} TeamA vs TeamB"
            market_type = random.choice(market_types)
            bookmaker = random.choice(['Bet365', 'William Hill', 'Pinnacle', 'Betfair'])
            
            # Generar odds según mercado
            odds_data = StressTestDataGenerator._generate_odds(market_type)
            
            # Timestamp con variación
            timestamp = base_time - timedelta(seconds=random.randint(0, 3600))
            
            snapshot = Snapshot(
                event_id=event_id,
                event_name=event_name,
                market_type=market_type,
                bookmaker=bookmaker,
                odds_data=odds_data,
                timestamp=timestamp,
                source="stress_test"
            )
            snapshots.append(snapshot)
        
        return snapshots
    
    @staticmethod
    def _generate_odds(market_type: str) -> dict:
        """Genera odds aleatorios para un mercado específico"""
        if market_type == '1X2':
            return {
                '1': round(random.uniform(1.5, 5.0), 2),
                'X': round(random.uniform(2.0, 6.0), 2),
                '2': round(random.uniform(1.5, 5.0), 2)
            }
        elif market_type == 'Over/Under':
            line = random.choice([0.5, 1.5, 2.5, 3.5])
            return {
                f'Over {line}': round(random.uniform(1.2, 3.0), 2),
                f'Under {line}': round(random.uniform(1.2, 3.0), 2)
            }
        elif market_type == 'Asian Handicap':
            handicap = random.choice([-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0])
            return {
                f'Home {handicap:+.2f}': round(random.uniform(1.3, 4.0), 2),
                f'Away {handicap:+.2f}': round(random.uniform(1.3, 4.0), 2)
            }
        elif market_type == 'Double Chance':
            return {
                '1X': round(random.uniform(1.1, 2.5), 2),
                'X2': round(random.uniform(1.1, 2.5), 2),
                '12': round(random.uniform(1.1, 2.5), 2)
            }
        else:
            return {'1': 2.0, 'X': 3.0, '2': 2.5}

class TestStress:
    """Pruebas de estrés del sistema QuantBet"""
    
    @pytest.fixture
    def temp_db(self):
        """Crea una base de datos temporal para los tests"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        # Aplicar migraciones
        apply_migrations(db_path)
        
        yield db_path
        
        # Limpiar
        Path(db_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def repo(self, temp_db):
        """Repositorio con base de datos temporal"""
        return Repository(temp_db)
    
    @pytest.fixture
    def generator(self):
        """Generador de datos de estrés"""
        return StressTestDataGenerator()
    
    def test_generate_1000_snapshots(self, generator, repo):
        """Genera 1000 snapshots y verifica almacenamiento"""
        snapshots = generator.generate_snapshots(1000)
        assert len(snapshots) == 1000
        
        # Guardar en lote
        start_time = time.time()
        count = repo.save_snapshots_batch(snapshots)
        elapsed = time.time() - start_time
        
        assert count == 1000
        print(f"\n[STRESS] 1000 snapshots guardados en {elapsed:.2f} segundos")
        print(f"[STRESS] Velocidad: {1000/elapsed:.0f} snapshots/segundo")
        
        # Verificar que se guardaron
        stats = repo.get_db_stats()
        assert stats['snapshots']['total'] == 1000
    
    def test_generate_5000_snapshots(self, generator, repo):
        """Genera 5000 snapshots para prueba de escalabilidad"""
        snapshots = generator.generate_snapshots(5000)
        
        start_time = time.time()
        count = repo.save_snapshots_batch(snapshots)
        elapsed = time.time() - start_time
        
        assert count == 5000
        print(f"\n[STRESS] 5000 snapshots guardados en {elapsed:.2f} segundos")
        print(f"[STRESS] Velocidad: {5000/elapsed:.0f} snapshots/segundo")
        
        # Verificar estadísticas
        stats = repo.get_db_stats()
        assert stats['snapshots']['total'] == 5000
        
        # Verificar índices funcionando
        # Consulta rápida con índice
        start_time = time.time()
        latest = repo.get_latest_snapshots(limit=100)
        elapsed = time.time() - start_time
        
        print(f"[STRESS] 100 últimos snapshots consultados en {elapsed:.4f} segundos")
        assert len(latest) == 100
        assert elapsed < 0.5  # Debe ser rápido con índices
    
    def test_arbitrage_with_1000_events(self, generator, repo):
        """Ejecuta arbitraje con 1000 eventos"""
        snapshots = generator.generate_snapshots(1000)
        repo.save_snapshots_batch(snapshots)
        
        # Inicializar motor
        engine = ArbitrageEngine()
        scorer = OpportunityScorer()
        
        start_time = time.time()
        
        # Procesar todos los snapshots
        total_opportunities = 0
        total_decisions = 0
        
        for snapshot in snapshots:
            opportunities = engine.find_opportunities(snapshot)
            total_opportunities += len(opportunities)
            
            for opp in opportunities:
                score = scorer.score_opportunity(opp)
                if score > 50:  # Solo guardar decisiones relevantes
                    decision = Decision(
                        event_id=opp.event_id,
                        strategy="arbitrage",
                        opportunity_data=opp.to_dict(),
                        decision_data={"score": score},
                        opportunity_score=score,
                        timestamp=datetime.now(),
                        executed=False
                    )
                    repo.save_decision(decision)
                    total_decisions += 1
        
        elapsed = time.time() - start_time
        
        print(f"\n[STRESS] 1000 eventos procesados en {elapsed:.2f} segundos")
        print(f"[STRESS] Oportunidades encontradas: {total_opportunities}")
        print(f"[STRESS] Decisiones guardadas: {total_decisions}")
        print(f"[STRESS] Velocidad: {1000/elapsed:.0f} eventos/segundo")
        
        # Verificar que hay decisiones
        assert total_decisions > 0
        
        # Verificar estadísticas
        stats = repo.get_db_stats()
        assert stats['snapshots']['total'] == 1000
        assert stats['decisions']['total'] > 0
    
    def test_all_strategies_with_1000_events(self, generator, repo):
        """Ejecuta todas las estrategias con 1000 eventos"""
        snapshots = generator.generate_snapshots(1000)
        repo.save_snapshots_batch(snapshots)
        
        # Inicializar componentes
        engine = ArbitrageEngine()
        scorer = OpportunityScorer()
        value_detector = ValueBetDetector()
        dutching_calculator = DutchingCalculator()
        model = ProbabilityModelFactory.get_model('historical')
        
        start_time = time.time()
        
        total_arbitrage = 0
        total_value = 0
        total_dutching = 0
        
        for snapshot in snapshots:
            # Arbitraje
            opportunities = engine.find_opportunities(snapshot)
            for opp in opportunities:
                score = scorer.score_opportunity(opp)
                if score > 50:
                    repo.save_decision(Decision(
                        event_id=opp.event_id,
                        strategy="arbitrage",
                        opportunity_data=opp.to_dict(),
                        decision_data={"score": score},
                        opportunity_score=score,
                        timestamp=datetime.now(),
                        executed=False
                    ))
                    total_arbitrage += 1
            
            # Value Betting
            fair_prob = model.predict(snapshot)
            if fair_prob:
                value_bets = value_detector.detect(snapshot, fair_prob)
                for bet in value_bets:
                    if bet.get('score', 0) > 50:
                        repo.save_decision(Decision(
                            event_id=snapshot.event_id,
                            strategy="value_betting",
                            opportunity_data=bet,
                            decision_data={"edge": bet.get('edge_percent', 0)},
                            opportunity_score=bet.get('score', 0),
                            timestamp=datetime.now(),
                            executed=False
                        ))
                        total_value += 1
            
            # Dutching
            odds_list = list(snapshot.odds_data.values()) if snapshot.odds_data else []
            if len(odds_list) >= 2:
                dutching_results = dutching_calculator.calculate_stakes(odds_list)
                if dutching_results and dutching_results.get('stakes'):
                    repo.save_decision(Decision(
                        event_id=snapshot.event_id,
                        strategy="dutching",
                        opportunity_data={"odds": odds_list},
                        decision_data=dutching_results,
                        opportunity_score=50.0,
                        timestamp=datetime.now(),
                        executed=False
                    ))
                    total_dutching += 1
        
        elapsed = time.time() - start_time
        
        print(f"\n[STRESS] Pipeline completo con 1000 eventos: {elapsed:.2f} segundos")
        print(f"[STRESS] Arbitraje: {total_arbitrage} decisiones")
        print(f"[STRESS] Value Betting: {total_value} decisiones")
        print(f"[STRESS] Dutching: {total_dutching} decisiones")
        print(f"[STRESS] Total: {total_arbitrage + total_value + total_dutching} decisiones")
        print(f"[STRESS] Velocidad: {1000/elapsed:.0f} eventos/segundo")
        
        # Verificar estadísticas
        stats = repo.get_db_stats()
        assert stats['snapshots']['total'] == 1000
        assert stats['decisions']['total'] > 0
        
        # Verificar por estrategia
        by_strategy = stats['decisions']['by_strategy']
        assert 'arbitrage' in by_strategy or total_arbitrage == 0
        assert 'value_betting' in by_strategy or total_value == 0
        assert 'dutching' in by_strategy or total_dutching == 0
    
    def test_market_summary_performance(self, generator, repo):
        """Prueba el rendimiento de market_summary con muchos datos"""
        snapshots = generator.generate_snapshots(2000)
        repo.save_snapshots_batch(snapshots)
        
        # Generar algunas decisiones para actualizar el resumen
        engine = ArbitrageEngine()
        scorer = OpportunityScorer()
        
        for snapshot in snapshots[:100]:  # Solo 100 para no tardar demasiado
            opportunities = engine.find_opportunities(snapshot)
            for opp in opportunities[:3]:  # Máximo 3 por snapshot
                score = scorer.score_opportunity(opp)
                if score > 50:
                    repo.update_market_summary(
                        event_id=opp.event_id,
                        market_type=snapshot.market_type,
                        best_opportunity=score,
                        total_opportunities=1,
                        avg_score=score
                    )
        
        # Medir tiempo de consulta del resumen
        start_time = time.time()
        summary = repo.get_market_summary(limit=50)
        elapsed = time.time() - start_time
        
        print(f"\n[STRESS] Market summary consultado en {elapsed:.4f} segundos")
        print(f"[STRESS] Resúmenes encontrados: {len(summary)}")
        
        # Debe ser muy rápido (menos de 0.1s)
        assert elapsed < 0.1
    
    def test_cleanup_performance(self, generator, repo):
        """Prueba el rendimiento de cleanup con datos antiguos"""
        # Generar datos con fechas antiguas
        snapshots = []
        base_time = datetime.now() - timedelta(days=60)
        
        for i in range(1000):
            event_id = f"event_{i:05d}"
            snapshot = Snapshot(
                event_id=event_id,
                event_name=f"Old Match {i}",
                market_type='1X2',
                bookmaker='Test',
                odds_data={'1': 2.0, 'X': 3.0, '2': 2.5},
                timestamp=base_time + timedelta(seconds=i),
                source="stress_old"
            )
            snapshots.append(snapshot)
        
        repo.save_snapshots_batch(snapshots)
        
        # Medir tiempo de cleanup
        start_time = time.time()
        repo.cleanup_old_data(days_to_keep=30)
        elapsed = time.time() - start_time
        
        print(f"\n[STRESS] Cleanup de 1000 snapshots antiguos en {elapsed:.2f} segundos")
        
        # Verificar que se eliminaron
        stats = repo.get_db_stats()
        print(f"[STRESS] Snapshots restantes: {stats['snapshots']['total']}")
        assert stats['snapshots']['total'] < 1000
    
    def test_concurrent_operations(self, generator, repo):
        """Prueba operaciones concurrentes (simuladas)"""
        snapshots = generator.generate_snapshots(500)
        repo.save_snapshots_batch(snapshots)
        
        # Simular múltiples operaciones en secuencia rápida
        start_time = time.time()
        
        operations = 0
        for i in range(100):
            # Lectura
            latest = repo.get_latest_snapshots(limit=10)
            assert len(latest) <= 10
            
            # Escritura
            if i % 2 == 0:
                snapshot = generator.generate_snapshots(1)[0]
                repo.save_snapshot(snapshot)
            
            # Actualización de resumen
            if i % 3 == 0:
                repo.update_market_summary(
                    event_id=f"event_{i}",
                    market_type='1X2',
                    best_opportunity=80.0,
                    total_opportunities=5,
                    avg_score=75.0
                )
            
            operations += 1
        
        elapsed = time.time() - start_time
        
        print(f"\n[STRESS] 100 operaciones concurrentes simuladas en {elapsed:.2f} segundos")
        print(f"[STRESS] Velocidad: {operations/elapsed:.0f} ops/segundo")
        
        # Verificar integridad
        stats = repo.get_db_stats()
        assert stats['snapshots']['total'] > 500