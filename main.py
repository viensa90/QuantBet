#!/usr/bin/env python3
"""
QuantBet - Pipeline Principal
Sistema de detección y decisión de oportunidades de arbitraje.
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


class QuantBetPipeline:
    """
    Pipeline principal de QuantBet.
    
    Orquesta 7 pasos secuenciales:
    1. Obtener snapshots del proveedor
    2. Persistir snapshots en SQLite
    3. Agrupar snapshots por evento
    4. Detectar oportunidades de arbitraje
    5. Puntuar oportunidades
    6. Generar decisiones (con validación de bankroll)
    7. Persistir decisiones y generar reporte
    """
    
    def __init__(self, csv_path: str = None, threshold: float = None):
        """
        Inicializa el pipeline con configuración desde YAML.
        
        Args:
            csv_path: Ruta al archivo CSV (None = usar config.yaml)
            threshold: Umbral de decisión (None = usar config.yaml)
        """
        # Cargar configuración
        self.config = ConfigLoader()
        self.csv_path = csv_path or self.config.csv_path
        self.threshold = threshold if threshold is not None else self.config.decision_threshold
        
        # Configurar logging
        self.logger = setup_logging(
            level=self.config.logging_level,
            log_format=self.config.logging_format,
            log_file=self.config.logging_file
        )
        
        # Inicializar componentes
        self.db = Database()
        self.repository = Repository(self.db)
        self.provider = CSVProvider(self.csv_path)
        self.engine = ArbitrageEngine()
        self.scorer = OpportunityScorer(**self.config.scoring_weights)
        self.bankroll = BankrollManager(
            total_bankroll=self.config.bankroll_total,
            max_exposure=self.config.bankroll_max_exposure
        )
        
        self.logger.info("QuantBet Pipeline inicializado")
        self.logger.info(f"Umbral de decisión: {self.threshold}")
        self.logger.info(f"Bankroll total: ${self.bankroll.total_bankroll:.2f}")
        
    def run(self, event_filter: str = None) -> Dict[str, Any]:
        """
        Ejecuta el pipeline completo.
        
        Args:
            event_filter: ID de evento específico (None = todos)
            
        Returns:
            Dict con resultados del pipeline
        """
        self.logger.info("="*60)
        self.logger.info("QuantBet Pipeline v0.1.0 - Iniciando ejecución")
        self.logger.info(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("="*60)
        
        # Paso 1: Obtener snapshots
        self.logger.info("[1/7] Obteniendo snapshots del proveedor...")
        snapshots = self.provider.get_snapshots()
        self.logger.info(f"  ✅ {len(snapshots)} snapshots obtenidos")
        
        # Paso 2: Persistir snapshots (INSERT, nunca UPDATE)
        self.logger.info("[2/7] Persistiendo snapshots en SQLite...")
        persisted_count = 0
        for snapshot in snapshots:
            if event_filter and snapshot.event_id != event_filter:
                continue
            self.repository.insert_snapshot(snapshot)
            persisted_count += 1
        self.logger.info(f"  ✅ {persisted_count} snapshots persistidos (inmutables)")
        
        # Paso 3: Agrupar por evento
        self.logger.info("[3/7] Agrupando snapshots por evento...")
        snapshots_by_event = self._group_by_event(snapshots, event_filter)
        self.logger.info(f"  ✅ {len(snapshots_by_event)} eventos encontrados")
        
        # Paso 4: Detectar oportunidades
        self.logger.info("[4/7] Detectando oportunidades de arbitraje...")
        opportunities = []
        for event_id, event_snapshots in snapshots_by_event.items():
            event_opportunities = self.engine.detect_opportunities(
                event_id, event_snapshots
            )
            opportunities.extend(event_opportunities)
        self.logger.info(f"  ✅ {len(opportunities)} oportunidades detectadas")
        
        # Paso 5: Puntuar oportunidades
        self.logger.info("[5/7] Puntuando oportunidades...")
        scored_opportunities = []
        for opp in opportunities:
            scored_opp = self.scorer.score(opp)
            scored_opportunities.append(scored_opp)
        self.logger.info(f"  ✅ {len(scored_opportunities)} oportunidades puntuadas")
        
        # Paso 6: Generar decisiones con validación de bankroll
        self.logger.info(f"[6/7] Generando decisiones (umbral: {self.threshold})...")
        decisions = self._generate_decisions(scored_opportunities)
        self.logger.info(f"  ✅ {len(decisions)} decisiones generadas")
        
        # Paso 7: Persistir decisiones y reporte
        self.logger.info("[7/7] Persistiendo decisiones y generando reporte...")
        for decision in decisions:
            self.repository.insert_decision(decision)
        self.logger.info(f"  ✅ {len(decisions)} decisiones persistidas (auditables)")
        
        # Generar reporte
        self._generate_report(snapshots, opportunities, decisions)
        
        return {
            "snapshots_count": len(snapshots),
            "events_count": len(snapshots_by_event),
            "opportunities_count": len(opportunities),
            "decisions_count": len(decisions),
            "decisions": decisions
        }
    
    def _generate_decisions(self, scored_opportunities: List) -> List[Dict]:
        """
        Genera decisiones con validación de bankroll.
        
        Args:
            scored_opportunities: Oportunidades puntuadas
            
        Returns:
            Lista de decisiones
        """
        decisions = []
        
        for opp in scored_opportunities:
            base_action = "EJECUTAR" if opp.score >= self.threshold else "SALTAR"
            
            # Si es EJECUTAR, validar bankroll
            if base_action == "EJECUTAR":
                valid, message, stakes = self.bankroll.validate(opp)
                if not valid:
                    action = "SALTAR"
                    reason = f"Bankroll: {message}"
                    self.logger.warning(f"  ⚠️  {opp.event_id}: {reason}")
                else:
                    action = "EJECUTAR"
                    reason = "Fondos validados"
                    self.logger.info(f"  ✅ {opp.event_id}: {reason} - Inversión requerida: ${sum(s['stake'] for s in stakes.values()):.2f}")
            else:
                action = "SALTAR"
                reason = f"Score {opp.score:.1f} < umbral {self.threshold}"
                stakes = {}
            
            decision = {
                "opportunity_id": opp.id,
                "event_id": opp.event_id,
                "action": action,
                "score": opp.score,
                "threshold": self.threshold,
                "reason": reason,
                "stakes": stakes,
                "timestamp": datetime.now().isoformat()
            }
            decisions.append(decision)
        
        return decisions
    
    def _group_by_event(self, snapshots: List, event_filter: str = None) -> Dict:
        """Agrupa snapshots por event_id."""
        grouped = {}
        for snapshot in snapshots:
            if event_filter and snapshot.event_id != event_filter:
                continue
            if snapshot.event_id not in grouped:
                grouped[snapshot.event_id] = []
            grouped[snapshot.event_id].append(snapshot)
        return grouped
    
    def list_events(self) -> List[str]:
        """Lista todos los eventos disponibles en el CSV."""
        snapshots = self.provider.get_snapshots()
        events = list(set(s.event_id for s in snapshots))
        return sorted(events)
    
    def _generate_report(self, snapshots: List, opportunities: List, decisions: List):
        """Genera reporte legible en consola."""
        self.logger.info("="*60)
        self.logger.info("📋 REPORTE FINAL")
        self.logger.info("="*60)
        
        # Resumen
        execute_count = sum(1 for d in decisions if d["action"] == "EJECUTAR")
        skip_count = sum(1 for d in decisions if d["action"] == "SALTAR")
        
        self.logger.info("📈 Resumen:")
        self.logger.info(f"   Total snapshots: {len(snapshots)}")
        self.logger.info(f"   Oportunidades: {len(opportunities)}")
        self.logger.info(f"   EJECUTAR: {execute_count}")
        self.logger.info(f"   SALTAR: {skip_count}")
        self.logger.info(f"   Bankroll disponible: ${self.bankroll.available:.2f}")
        
        # Detalle de oportunidades
        if opportunities:
            self.logger.info("🎲 Oportunidades detectadas:")
            for opp in opportunities:
                self.logger.info(f"   • {opp.event_id}: {opp.market} - Surebet {opp.roi:.2f}%")
                self.logger.info(f"     Score: {opp.score:.1f}/100 → ", extra={"end": ""})
                for d in decisions:
                    if d["opportunity_id"] == opp.id:
                        self.logger.info(f"{d['action']} ({d['reason']})")
                        break
        
        # Top recomendaciones
        execute_decisions = [d for d in decisions if d["action"] == "EJECUTAR"]
        if execute_decisions:
            self.logger.info("🚀 Recomendaciones para ejecutar:")
            for d in execute_decisions:
                for opp in opportunities:
                    if opp.id == d["opportunity_id"]:
                        self.logger.info(f"   • {opp.event_id}: ROI {opp.roi:.2f}% - Score {opp.score:.1f}")
                        if d["stakes"]:
                            for selection, stake_info in d["stakes"].items():
                                self.logger.info(f"     - {selection}: ${stake_info['stake']:.2f} @ {stake_info['odds']} ({stake_info['bookmaker']})")
                        break
        
        self.logger.info("="*60)


def main():
    """Punto de entrada CLI."""
    parser = argparse.ArgumentParser(
        description="QuantBet - Sistema de Arbitraje Deportivo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py                    # Ejecutar pipeline completo
  python main.py --event EVT-003    # Filtrar por evento
  python main.py --list-events      # Listar eventos disponibles
  python main.py --csv datos.csv    # Usar CSV personalizado
  python main.py --threshold 70     # Cambiar umbral de decisión
        """
    )
    
    parser.add_argument(
        "--event", "-e",
        type=str,
        help="Filtrar por ID de evento específico"
    )
    
    parser.add_argument(
        "--csv", "-c",
        type=str,
        help="Ruta a archivo CSV personalizado"
    )
    
    parser.add_argument(
        "--list-events", "-l",
        action="store_true",
        help="Listar eventos disponibles y salir"
    )
    
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        help="Umbral de decisión (default: desde config.yaml)"
    )
    
    args = parser.parse_args()
    
    # Inicializar pipeline
    pipeline = QuantBetPipeline(
        csv_path=args.csv,
        threshold=args.threshold
    )
    
    # Listar eventos
    if args.list_events:
        events = pipeline.list_events()
        logger = get_logger()
        logger.info(f"📅 Eventos disponibles ({len(events)}):")
        for event in events:
            logger.info(f"   • {event}")
        return 0
    
    # Ejecutar pipeline
    try:
        result = pipeline.run(event_filter=args.event)
        
        # Código de salida según decisiones
        execute_count = sum(1 for d in result["decisions"] if d["action"] == "EJECUTAR")
        logger = get_logger()
        if execute_count > 0:
            logger.info(f"✅ Pipeline completado: {execute_count} oportunidades para ejecutar")
            return 0
        else:
            logger.warning("⚠️  Pipeline completado: sin oportunidades que ejecutar")
            return 0
            
    except Exception as e:
        logger = get_logger()
        logger.error(f"❌ Error en el pipeline: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())