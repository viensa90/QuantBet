# main.py
"""
QuantBet MVP - Pipeline Principal
Flujo: CSV Provider → Motor Arbitraje → Scorer → SQLite → Reporte
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import List

# Agregar directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent))

from src.connectors import CSVProvider
from src.core.arbitrage import ArbitrageEngine
from src.core.scorer import OpportunityScorer
from src.storage import DatabaseManager, Repository
from src.domain.entities import Decision


class QuantBetPipeline:
    """
    Orquesta el pipeline completo de QuantBet.
    
    Principios:
    - Los Conectores solo obtienen datos, nunca deciden.
    - El Motor Matemático no conoce la fuente de datos.
    - Toda decisión es auditable (persistida en SQLite).
    """
    
    def __init__(self, csv_path: str = "data/sample_events.csv"):
        """Inicializa todos los componentes del pipeline."""
        self.provider = CSVProvider(csv_path)
        self.engine = ArbitrageEngine()
        self.scorer = OpportunityScorer()
        self.db = DatabaseManager()
        self.repo = Repository(self.db)
        
        print(f"✅ QuantBet Pipeline inicializado")
        print(f"   Proveedor: {self.provider.get_provider_name()}")
        print(f"   DB: {self.db.db_path}")
    
    def run(self, event_id: str = None) -> List[Decision]:
        """
        Ejecuta el pipeline completo.
        
        Args:
            event_id: Opcional. Filtrar por evento específico.
            
        Returns:
            Lista de Decisiones generadas y persistidas.
        """
        print("\n" + "=" * 60)
        print("🚀 EJECUTANDO PIPELINE QUANTBET")
        print("=" * 60)
        
        # Paso 1: Obtener snapshots del proveedor
        print("\n📡 Paso 1: Obteniendo datos del proveedor...")
        snapshots = self.provider.fetch_snapshots(event_id=event_id)
        print(f"   Snapshots obtenidos: {len(snapshots)}")
        
        if not snapshots:
            print("   ⚠️  No se encontraron snapshots. Abortando.")
            return []
        
        # Paso 2: Persistir snapshots (inmutables)
        print("\n💾 Paso 2: Persistiendo snapshots...")
        saved_snapshots = 0
        for snap in snapshots:
            try:
                self.repo.save_snapshot(snap)
                saved_snapshots += 1
            except Exception as e:
                print(f"   ⚠️  Error guardando {snap.snapshot_id}: {e}")
        print(f"   Snapshots guardados: {saved_snapshots}/{len(snapshots)}")
        
        # Paso 3: Agrupar snapshots por evento
        events = self._group_by_event(snapshots)
        print(f"\n📊 Paso 3: Eventos a analizar: {len(events)}")
        
        # Paso 4: Detectar oportunidades por evento
        print("\n🔍 Paso 4: Buscando oportunidades de arbitraje...")
        all_opportunities = []
        
        for evt_id, evt_snapshots in events.items():
            opportunities = self.engine.detect_arbitrage(evt_snapshots)
            if opportunities:
                print(f"   ✅ {evt_id}: {len(opportunities)} oportunidad(es)")
                all_opportunities.extend(opportunities)
            else:
                print(f"   ❌ {evt_id}: Sin oportunidades")
        
        if not all_opportunities:
            print("\n📊 No se encontraron oportunidades de arbitraje.")
            return []
        
        # Paso 5: Puntuar oportunidades
        print(f"\n⭐ Paso 5: Puntuando {len(all_opportunities)} oportunidades...")
        scored_opportunities = []
        
        for opp in all_opportunities:
            scored = self.scorer.score_opportunity(opp)
            scored_opportunities.append(scored)
            print(f"   {scored.event_id}: Score {scored.opportunity_score:.1f}/100")
        
        # Paso 6: Generar decisiones
        print("\n🎯 Paso 6: Generando decisiones...")
        decisions = []
        
        for scored_opp in scored_opportunities:
            # Aplicar umbral mínimo (configurable vía config.yaml)
            min_score = 60.0  # Umbral mínimo para ejecutar
            
            if scored_opp.opportunity_score >= min_score:
                decision = Decision(
                    decision_id=f"DEC-{scored_opp.event_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    event_id=scored_opp.event_id,
                    opportunity=scored_opp,
                    action="EXECUTE",
                    timestamp=datetime.now(),
                    reason=f"Score {scored_opp.opportunity_score:.1f} >= {min_score}"
                )
                decisions.append(decision)
                print(f"   ✅ {decision.decision_id}: EJECUTAR (Score: {scored_opp.opportunity_score:.1f})")
            else:
                decision = Decision(
                    decision_id=f"DEC-{scored_opp.event_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    event_id=scored_opp.event_id,
                    opportunity=scored_opp,
                    action="SKIP",
                    timestamp=datetime.now(),
                    reason=f"Score {scored_opp.opportunity_score:.1f} < {min_score}"
                )
                decisions.append(decision)
                print(f"   ⏭️  {decision.decision_id}: SALTAR (Score: {scored_opp.opportunity_score:.1f})")
        
        # Paso 7: Persistir decisiones (auditables)
        print("\n📝 Paso 7: Persistiendo decisiones...")
        saved_decisions = 0
        for dec in decisions:
            try:
                self.repo.save_decision(dec)
                saved_decisions += 1
            except Exception as e:
                print(f"   ⚠️  Error guardando {dec.decision_id}: {e}")
        print(f"   Decisiones guardadas: {saved_decisions}/{len(decisions)}")
        
        # Paso 8: Generar reporte
        self._generate_report(decisions)
        
        return decisions
    
    def _group_by_event(self, snapshots):
        """Agrupa snapshots por event_id."""
        events = {}
        for snap in snapshots:
            if snap.event_id not in events:
                events[snap.event_id] = []
            events[snap.event_id].append(snap)
        return events
    
    def _generate_report(self, decisions: List[Decision]):
        """Genera reporte final de decisiones."""
        print("\n" + "=" * 60)
        print("📊 REPORTE FINAL QUANTBET")
        print("=" * 60)
        
        execute_decisions = [d for d in decisions if d.action == "EXECUTE"]
        skip_decisions = [d for d in decisions if d.action == "SKIP"]
        
        print(f"\n🎯 Decisiones de EJECUCIÓN: {len(execute_decisions)}")
        for dec in execute_decisions:
            print(f"   • {dec.event_id}")
            print(f"     ROI Esperado: {dec.opportunity.expected_return:.2%}")
            print(f"     Score: {dec.opportunity.opportunity_score:.1f}/100")
            print(f"     Mejores cuotas: {dec.opportunity.best_odds}")
        
        print(f"\n⏭️  Decisiones SALTADAS: {len(skip_decisions)}")
        for dec in skip_decisions:
            print(f"   • {dec.event_id}: {dec.reason}")
        
        print(f"\n📈 Total decisiones: {len(decisions)}")
        print(f"✅ Pipeline completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)


def main():
    """Punto de entrada principal del MVP."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="QuantBet MVP - Detección de Oportunidades de Arbitraje"
    )
    parser.add_argument(
        "--event", "-e",
        type=str,
        help="Filtrar por event_id específico"
    )
    parser.add_argument(
        "--csv", "-c",
        type=str,
        default="data/sample_events.csv",
        help="Ruta al archivo CSV de datos"
    )
    parser.add_argument(
        "--list-events", "-l",
        action="store_true",
        help="Listar eventos disponibles y salir"
    )
    
    args = parser.parse_args()
    
    # Modo listado de eventos
    if args.list_events:
        provider = CSVProvider(args.csv)
        events = provider.get_available_events()
        print("\n📊 Eventos disponibles:")
        for evt in events:
            snapshots = provider.fetch_snapshots(event_id=evt)
            bookmakers = set(s.bookmaker_name for s in snapshots)
            print(f"   • {evt}")
            print(f"     Snapshots: {len(snapshots)}")
            print(f"     Bookmakers: {', '.join(bookmakers)}")
        return
    
    # Ejecutar pipeline
    pipeline = QuantBetPipeline(csv_path=args.csv)
    decisions = pipeline.run(event_id=args.event)
    
    # Código de salida
    execute_count = len([d for d in decisions if d.action == "EXECUTE"])
    if execute_count > 0:
        print(f"\n🎉 Se encontraron {execute_count} oportunidades ejecutables!")
        sys.exit(0)
    else:
        print("\n📊 No se encontraron oportunidades ejecutables.")
        sys.exit(1)


if __name__ == "__main__":
    main()