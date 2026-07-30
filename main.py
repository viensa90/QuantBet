#!/usr/bin/env python3
"""
QuantBet - Pipeline Principal
Sistema de detección y decisión de oportunidades de arbitraje, value betting y dutching.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

from src.config_loader import ConfigLoader
from src.logger import setup_logging, get_logger
from src.storage.database import Database
from src.storage.repository import Repository
from src.connectors.csv_provider import CSVProvider
from src.core.arbitrage import ArbitrageEngine
from src.core.scorer import OpportunityScorer
from src.core.bankroll import BankrollManager
from src.core.value_betting import ValueBetDetector
from src.core.dutching import DutchingCalculator


class QuantBetPipeline:
    """Pipeline principal con soporte para múltiples estrategias."""
    
    def __init__(self, csv_path: str = None, threshold: float = None):
        self.config = ConfigLoader()
        self.csv_path = csv_path or self.config.csv_path
        self.threshold = threshold if threshold is not None else self.config.decision_threshold
        
        self.logger = setup_logging(
            level=self.config.logging_level,
            log_format=self.config.logging_format,
            log_file=self.config.logging_file
        )
        
        self.db = Database()
        self.repository = Repository(self.db)
        self.provider = CSVProvider(self.csv_path)
        self.engine = ArbitrageEngine()
        self.scorer = OpportunityScorer(**self.config.scoring_weights)
        self.bankroll = BankrollManager(
            total_bankroll=self.config.bankroll_total,
            max_exposure=self.config.bankroll_max_exposure
        )
        self.value_detector = ValueBetDetector(margin=0.05)
        self.dutching_calc = DutchingCalculator()
        
        self.logger.info("QuantBet Pipeline inicializado con Value Betting y Dutching")
    
    def run(self, event_filter: str = None, mode: str = "arbitrage") -> Dict[str, Any]:
        """
        Ejecuta el pipeline en el modo especificado.
        
        Args:
            event_filter: ID de evento opcional
            mode: "arbitrage", "value", "dutching" o "all"
        """
        self.logger.info("="*60)
        self.logger.info(f"QuantBet Pipeline v0.1.0 - Modo: {mode}")
        self.logger.info(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("="*60)
        
        snapshots = self.provider.get_snapshots()
        if event_filter:
            snapshots = [s for s in snapshots if s.event_id == event_filter]
        
        self.logger.info(f"📊 {len(snapshots)} snapshots cargados")
        
        results = {"snapshots_count": len(snapshots)}
        
        if mode in ("arbitrage", "all"):
            results["arbitrage"] = self._run_arbitrage(snapshots)
        if mode in ("value", "all"):
            results["value_bets"] = self._run_value_betting(snapshots)
        if mode in ("dutching", "all"):
            results["dutching"] = self._run_dutching(snapshots)
        
        return results
    
    def _run_arbitrage(self, snapshots: List) -> Dict:
        """Ejecuta detección de arbitraje."""
        self.logger.info("[Arbitraje] Detectando oportunidades...")
        snapshots_by_event = self._group_by_event(snapshots)
        opportunities = []
        for event_id, event_snapshots in snapshots_by_event.items():
            opportunities.extend(self.engine.detect_opportunities(event_id, event_snapshots))
        
        self.logger.info(f"  ✅ {len(opportunities)} oportunidades de arbitraje")
        return {"opportunities": opportunities, "count": len(opportunities)}
    
    def _run_value_betting(self, snapshots: List) -> Dict:
        """Ejecuta detección de value bets con probabilidades justas de ejemplo."""
        self.logger.info("[Value Betting] Detectando value bets...")
        snapshots_by_event = self._group_by_event(snapshots)
        all_value_bets = []
        
        # Probabilidades justas de ejemplo (en un sistema real vendrían de un modelo)
        default_fair_probs = {"Local": 0.40, "Empate": 0.30, "Visitante": 0.30}
        
        for event_id, event_snaps in snapshots_by_event.items():
            value_bets = self.value_detector.detect(event_id, event_snaps, default_fair_probs)
            all_value_bets.extend(value_bets)
        
        self.logger.info(f"  ✅ {len(all_value_bets)} value bets encontradas")
        return {"value_bets": all_value_bets, "count": len(all_value_bets)}
    
    def _run_dutching(self, snapshots: List) -> Dict:
        """Ejecuta cálculo de dutching para eventos con múltiples selecciones."""
        self.logger.info("[Dutching] Calculando stakes...")
        snapshots_by_event = self._group_by_event(snapshots)
        dutching_results = []
        
        for event_id, event_snaps in snapshots_by_event.items():
            # Agrupar por mercado
            markets = {}
            for s in event_snaps:
                if s.market not in markets:
                    markets[s.market] = []
                markets[s.market].append(s)
            
            for market, m_snaps in markets.items():
                # Tomar la mejor cuota de cada selección
                best_by_selection = {}
                for s in m_snaps:
                    if s.selection not in best_by_selection or s.odds > best_by_selection[s.selection][1]:
                        best_by_selection[s.selection] = (s.bookmaker, s.odds)
                
                selections = [(sel, odds) for sel, (_, odds) in best_by_selection.items()]
                if len(selections) >= 2:
                    stake = 100.0  # Stake de ejemplo
                    result = self.dutching_calc.calculate(selections, stake)
                    dutching_results.append({
                        "event_id": event_id,
                        "market": market,
                        "calculation": result
                    })
        
        self.logger.info(f"  ✅ {len(dutching_results)} cálculos de dutching")
        return {"dutching_results": dutching_results, "count": len(dutching_results)}
    
    def _group_by_event(self, snapshots: List) -> Dict:
        """Agrupa snapshots por event_id."""
        grouped = {}
        for s in snapshots:
            if s.event_id not in grouped:
                grouped[s.event_id] = []
            grouped[s.event_id].append(s)
        return grouped
    
    def list_events(self) -> List[str]:
        """Lista eventos disponibles."""
        snapshots = self.provider.get_snapshots()
        return sorted(list(set(s.event_id for s in snapshots)))


def main():
    parser = argparse.ArgumentParser(description="QuantBet - Sistema de Arbitraje Deportivo")
    parser.add_argument("--event", "-e", type=str, help="Filtrar por ID de evento")
    parser.add_argument("--csv", "-c", type=str, help="CSV personalizado")
    parser.add_argument("--list-events", "-l", action="store_true", help="Listar eventos")
    parser.add_argument("--threshold", "-t", type=float, help="Umbral de decisión")
    parser.add_argument("--mode", "-m", type=str, default="arbitrage",
                        choices=["arbitrage", "value", "dutching", "all"],
                        help="Estrategia a ejecutar")
    
    args = parser.parse_args()
    
    pipeline = QuantBetPipeline(csv_path=args.csv, threshold=args.threshold)
    
    if args.list_events:
        events = pipeline.list_events()
        logger = get_logger()
        logger.info(f"📅 Eventos disponibles ({len(events)}):")
        for e in events:
            logger.info(f"   • {e}")
        return 0
    
    try:
        result = pipeline.run(event_filter=args.event, mode=args.mode)
        logger = get_logger()
        logger.info("✅ Pipeline completado")
        # Mostrar resumen breve
        for strategy, data in result.items():
            if strategy != "snapshots_count" and isinstance(data, dict) and "count" in data:
                logger.info(f"   {strategy}: {data['count']} encontrado(s)")
        return 0
    except Exception as e:
        logger = get_logger()
        logger.error(f"❌ Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())