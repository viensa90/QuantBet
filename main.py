#!/usr/bin/env python3
"""
QuantBet - Sistema de Arbitraje Deportivo Automatizado
CLI principal con soporte para múltiples estrategias y modos
Versión: 0.3.1 (Optimización de rendimiento + Notificaciones)
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# Configurar path para imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from src.config_loader import configLoader
config = ConfigLoader().config
from src.logger import setup_logging
from src.storage.database import get_db
from src.storage.repository import Repository
from src.storage.migrations import apply_migrations
from src.connectors.factory import ProviderFactory
from src.core.arbitrage import ArbitrageEngine
from src.core.scorer import OpportunityScorer
from src.core.value_betting import ValueBetDetector
from src.core.dutching import DutchingCalculator
from src.core.probability_model import ProbabilityModelFactory
from src.domain.entities import Decision, Opportunity, Snapshot
from src.notifications import NotificationManager

logger = logging.getLogger(__name__)

class QuantBetRunner:
    """Orquestador principal del sistema QuantBet"""
    
    def __init__(self, source: str = "csv", markets: Optional[List[str]] = None):
        self.source = source
        self.markets = markets or config.get('markets', {}).get('enabled', ['1X2'])
        self.repo = Repository()
        self.scorer = OpportunityScorer()
        self.notifier = NotificationManager()
        
        # Inicializar componentes según configuración
        self.arbitrage_engine = ArbitrageEngine()
        self.value_detector = ValueBetDetector()
        self.dutching_calculator = DutchingCalculator()
        
        # Modelo de probabilidad (para value betting)
        model_type = config.get('probability_model', {}).get('type', 'historical')
        self.probability_model = ProbabilityModelFactory.get_model(model_type)
        
        logger.info(f"QuantBetRunner inicializado con fuente: {source}, mercados: {markets}")
    
    def fetch_data(self) -> List[Snapshot]:
        """Obtiene datos del conector configurado"""
        provider = ProviderFactory.get_provider(self.source)
        snapshots = provider.fetch_snapshots()
        
        if not snapshots:
            logger.warning("No se obtuvieron datos del proveedor")
            return []
        
        logger.info(f"Obtenidos {len(snapshots)} snapshots")
        return snapshots
    
    def save_snapshots(self, snapshots: List[Snapshot]) -> int:
        """Guarda snapshots en lote y actualiza resumen"""
        if not snapshots:
            return 0
        
        # Guardar en lote
        count = self.repo.save_snapshots_batch(snapshots)
        logger.info(f"Guardados {count} snapshots en lote")
        
        return count
    
    def run_arbitrage(self, snapshots: List[Snapshot]) -> List[Decision]:
        """Ejecuta el motor de arbitraje"""
        decisions = []
        
        for snapshot in snapshots:
            # Filtrar por mercado si está especificado
            if snapshot.market_type not in self.markets:
                continue
            
            opportunities = self.arbitrage_engine.find_opportunities(snapshot)
            
            for opp in opportunities:
                score = self.scorer.score_opportunity(opp)
                decision = Decision(
                    event_id=opp.event_id,
                    strategy="arbitrage",
                    opportunity_data=opp.to_dict(),
                    decision_data={
                        "score": score,
                        "profit_percent": opp.profit_percent,
                        "market_type": opp.market_type
                    },
                    opportunity_score=score,
                    timestamp=datetime.now(),
                    executed=False
                )
                decisions.append(decision)
                
                logger.debug(f"Arbitraje: {opp.event_id} - Score: {score:.2f} - Profit: {opp.profit_percent:.2f}%")
        
        if decisions:
            self.repo.save_decisions_batch(decisions)
            self._update_market_summary(decisions)
            self._send_notifications(decisions)
            logger.info(f"Guardadas {len(decisions)} decisiones de arbitraje")
        
        return decisions
    
    def run_value_betting(self, snapshots: List[Snapshot]) -> List[Decision]:
        """Ejecuta el detector de value betting con modelo de probabilidad"""
        decisions = []
        
        for snapshot in snapshots:
            if snapshot.market_type not in self.markets:
                continue
            
            # Usar el modelo de probabilidad para calcular fair odds
            fair_prob = self.probability_model.predict(snapshot)
            if fair_prob is None:
                continue
            
            # Detectar value bets
            value_bets = self.value_detector.detect(snapshot, fair_prob)
            
            for bet in value_bets:
                decision = Decision(
                    event_id=snapshot.event_id,
                    strategy="value_betting",
                    opportunity_data={
                        "market_type": snapshot.market_type,
                        "selection": bet.get("selection", "unknown"),
                        "odds": bet.get("odds", 0.0),
                        "implied_prob": bet.get("implied_prob", 0.0),
                        "fair_prob": bet.get("fair_prob", 0.0),
                        "model": self.probability_model.__class__.__name__
                    },
                    decision_data={
                        "value": bet.get("value", 0.0),
                        "edge_percent": bet.get("edge_percent", 0.0)
                    },
                    opportunity_score=bet.get("score", 0.0),
                    timestamp=datetime.now(),
                    executed=False
                )
                decisions.append(decision)
                
                logger.debug(f"Value Bet: {bet.get('selection')} - Edge: {bet.get('edge_percent', 0):.2f}%")
        
        if decisions:
            self.repo.save_decisions_batch(decisions)
            self._update_market_summary(decisions)
            self._send_notifications(decisions)
            logger.info(f"Guardadas {len(decisions)} decisiones de value betting")
        
        return decisions
    
    def run_dutching(self, snapshots: List[Snapshot]) -> List[Decision]:
        """Ejecuta el calculador de dutching"""
        decisions = []
        
        for snapshot in snapshots:
            if snapshot.market_type not in self.markets:
                continue
            
            # Extraer odds del snapshot
            odds_list = list(snapshot.odds_data.values()) if snapshot.odds_data else []
            
            # Necesitamos al menos 2 odds para dutching
            if len(odds_list) < 2:
                continue
            
            dutching_results = self.dutching_calculator.calculate_stakes(odds_list)
            
            if dutching_results and dutching_results.get("stakes"):
                decision = Decision(
                    event_id=snapshot.event_id,
                    strategy="dutching",
                    opportunity_data={
                        "market_type": snapshot.market_type,
                        "odds": odds_list,
                        "total_stake": dutching_results.get("total_stake", 0.0),
                        "selections": list(snapshot.odds_data.keys())
                    },
                    decision_data={
                        "stakes": dutching_results.get("stakes", []),
                        "guaranteed_return": dutching_results.get("guaranteed_return", 0.0),
                        "profit_margin": dutching_results.get("profit_margin", 0.0)
                    },
                    opportunity_score=dutching_results.get("score", 50.0),
                    timestamp=datetime.now(),
                    executed=False
                )
                decisions.append(decision)
                
                logger.debug(f"Dutching: {snapshot.event_id} - Return: {dutching_results.get('guaranteed_return', 0):.2f}")
        
        if decisions:
            self.repo.save_decisions_batch(decisions)
            self._update_market_summary(decisions)
            self._send_notifications(decisions)
            logger.info(f"Guardadas {len(decisions)} decisiones de dutching")
        
        return decisions
    
    def _update_market_summary(self, decisions: List[Decision]):
        """Actualiza el resumen de mercado para el dashboard"""
        for decision in decisions:
            # Extraer información de la decisión
            opp_data = decision.opportunity_data
            market_type = opp_data.get('market_type', 'unknown')
            
            # Obtener o calcular métricas
            best_opp = decision.opportunity_score
            total_opps = 1  # Por ahora 1, se puede mejorar con agregación
            
            self.repo.update_market_summary(
                event_id=decision.event_id,
                market_type=market_type,
                best_opportunity=best_opp,
                total_opportunities=total_opps,
                avg_score=best_opp
            )
    
    def _send_notifications(self, decisions: List[Decision]):
        """Envía notificaciones para decisiones de alto score"""
        if not decisions:
            return
        
        # Convertir a dict para el notificador
        decisions_dict = [
            {
                'event_id': d.event_id,
                'strategy': d.strategy,
                'score': d.opportunity_score,
                'data': d.opportunity_data,
                'timestamp': d.timestamp.isoformat()
            }
            for d in decisions
        ]
        
        # Enviar notificaciones
        self.notifier.check_and_notify(force=True)
    
    def run_all(self, snapshots: List[Snapshot]) -> dict:
        """Ejecuta todas las estrategias y retorna resumen"""
        results = {
            "arbitrage": len(self.run_arbitrage(snapshots)),
            "value_betting": len(self.run_value_betting(snapshots)),
            "dutching": len(self.run_dutching(snapshots)),
            "total_snapshots": len(snapshots),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Pipeline completo finalizado: {results}")
        return results
    
    def run_pipeline(self, mode: str = "all") -> dict:
        """Ejecuta el pipeline completo según modo"""
        # 1. Obtener datos
        snapshots = self.fetch_data()
        if not snapshots:
            return {"error": "No se obtuvieron datos", "snapshots": 0}
        
        # 2. Guardar snapshots en lote
        self.save_snapshots(snapshots)
        
        # 3. Ejecutar estrategias según modo
        if mode == "arbitrage":
            decisions = self.run_arbitrage(snapshots)
            return {"mode": "arbitrage", "decisions": len(decisions), "snapshots": len(snapshots)}
        elif mode == "value":
            decisions = self.run_value_betting(snapshots)
            return {"mode": "value_betting", "decisions": len(decisions), "snapshots": len(snapshots)}
        elif mode == "dutching":
            decisions = self.run_dutching(snapshots)
            return {"mode": "dutching", "decisions": len(decisions), "snapshots": len(snapshots)}
        else:  # all
            return self.run_all(snapshots)

def serve_dashboard():
    """Inicia el servidor web del dashboard"""
    logger.info("Iniciando dashboard web...")
    
    try:
        from src.web.app import app, init_app
        init_app()
        
        host = config.get('web', {}).get('host', '0.0.0.0')
        port = config.get('web', {}).get('port', 5000)
        debug = config.get('web', {}).get('debug', True)
        
        logger.info(f"Dashboard disponible en http://{host}:{port}")
        app.run(host=host, port=port, debug=debug)
    
    except ImportError as e:
        logger.error(f"Error al iniciar dashboard: {e}")
        logger.error("Asegúrate de que Flask y Jinja2 estén instalados")
        sys.exit(1)

def main():
    """Punto de entrada principal"""
    # Configurar logging
    setup_logging()
    
    # Aplicar migraciones al inicio
    logger.info("Verificando migraciones de base de datos...")
    try:
        apply_migrations()
        logger.info("Migraciones aplicadas correctamente")
    except Exception as e:
        logger.error(f"Error al aplicar migraciones: {e}")
        # Continuar de todas formas, puede que la BD ya esté actualizada
    
    parser = argparse.ArgumentParser(
        description='QuantBet - Sistema de Arbitraje Deportivo Automatizado v0.3.1',
        epilog='Ejemplos:\n  python main.py --mode arbitrage --source csv\n  python main.py --serve\n  python main.py --cleanup 30'
    )
    
    parser.add_argument('--mode', 
                       choices=['arbitrage', 'value', 'dutching', 'all'], 
                       default='all',
                       help='Modo de ejecución (default: all)')
    
    parser.add_argument('--source', 
                       choices=['csv', 'web'], 
                       default='csv',
                       help='Fuente de datos (default: csv)')
    
    parser.add_argument('--markets', 
                       nargs='+',
                       help='Mercados a analizar (ej: "1X2" "Over/Under")')
    
    parser.add_argument('--serve', 
                       action='store_true',
                       help='Iniciar dashboard web en lugar de ejecutar pipeline')
    
    parser.add_argument('--cleanup', 
                       type=int, 
                       default=0,
                       help='Limpiar datos antiguos (días a conservar)')
    
    parser.add_argument('--stats', 
                       action='store_true',
                       help='Mostrar estadísticas de la base de datos y salir')
    
    parser.add_argument('--notify', 
                       action='store_true',
                       help='Verificar y enviar notificaciones manualmente')
    
    parser.add_argument('--send-manual', 
                       nargs=2,
                       metavar=('EVENT_ID', 'STRATEGY'),
                       help='Enviar notificación manual para un evento (ej: event_001 all)')
    
    args = parser.parse_args()
    
    # Notificaciones manuales
    if args.notify:
        notifier = NotificationManager()
        sent = notifier.check_and_notify(force=True)
        print(f"\n✅ Notificaciones enviadas: {sent}")
        return
    
    if args.send_manual:
        event_id, strategy = args.send_manual
        notifier = NotificationManager()
        sent = notifier.send_manual_notification(event_id, strategy)
        if sent:
            print(f"\n✅ Notificación manual enviada para evento {event_id}")
        else:
            print(f"\n❌ No se pudo enviar notificación para evento {event_id}")
        return
    
    # Mostrar estadísticas
    if args.stats:
        repo = Repository()
        stats = repo.get_db_stats()
        print("\n=== ESTADÍSTICAS DE QuantBet ===\n")
        print(f"Snapshots totales: {stats['snapshots']['total']}")
        print(f"  Por mercado: {stats['snapshots']['by_market']}")
        print(f"  Último snapshot: {stats['snapshots']['last_timestamp']}")
        print(f"\nDecisiones totales: {stats['decisions']['total']}")
        print(f"  Por estrategia: {stats['decisions']['by_strategy']}")
        print(f"  Score promedio: {stats['decisions']['avg_score']}")
        print(f"\nResúmenes de mercado: {stats['summary']['total_markets']}")
        return
    
    # Limpiar datos antiguos
    if args.cleanup > 0:
        repo = Repository()
        repo.cleanup_old_data(days_to_keep=args.cleanup)
        logger.info(f"Limpieza completada: conservando {args.cleanup} días")
        return
    
    # Iniciar dashboard
    if args.serve:
        serve_dashboard()
        return
    
    # Ejecutar pipeline
    runner = QuantBetRunner(source=args.source, markets=args.markets)
    result = runner.run_pipeline(mode=args.mode)
    
    # Mostrar resumen
    print("\n=== RESUMEN DE EJECUCIÓN ===\n")
    for key, value in result.items():
        print(f"{key}: {value}")
    print(f"\nTimestamp: {datetime.now().isoformat()}")

if __name__ == '__main__':
    main()