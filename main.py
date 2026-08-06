#!/usr/bin/env python3
"""
QuantBet - Sistema de Arbitraje Deportivo Automatizado
CLI Principal - v0.3.3

Uso:
    python main.py --mode all --source csv
    python main.py --mode arbitrage --source web
    python main.py --serve
    python main.py --stats
    python main.py --cleanup 30
    python main.py --export results.json
"""

import argparse
import sys
import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

from src.config_loader import ConfigLoader
from src.logger import setup_logger
from src.storage.database import Database
from src.storage.repository import Repository
from src.core.arbitrage import ArbitrageEngine
from src.core.value_betting import ValueBetDetector
from src.core.dutching import DutchingCalculator
from src.core.scorer import OpportunityScorer  # ✅ CORREGIDO
from src.core.bankroll import BankrollManager
from src.connectors.csv_provider import CSVProvider
from src.connectors.web_provider import WebProvider
from src.connectors.factory import ConnectorFactory  # ✅ CORREGIDO
from src.domain.entities import Event, Market, Opportunity, Snapshot

# Cargar configuración
config = ConfigLoader().config
logger = setup_logger("quantbet")


def run_arbitrage(snapshots: List[Snapshot]) -> List[Dict]:
    """
    Ejecutar motor de arbitraje sobre snapshots.
    
    Args:
        snapshots: Lista de Snapshots inmutables
    
    Returns:
        Lista de oportunidades de arbitraje
    """
    logger.info("🔄 Ejecutando motor de arbitraje...")
    
    engine = ArbitrageEngine()
    opportunities = engine.detect_opportunities(snapshots)  # ✅ CORREGIDO
    
    # Convertir a dict para mantener compatibilidad
    result = [opp.to_dict() for opp in opportunities]
    
    # Filtrar por umbral mínimo de beneficio
    min_profit = config.get("thresholds", {}).get("min_profit_percent", 1.5)
    result = [o for o in result if o.get("profit_percent", 0) >= min_profit]
    
    logger.info(f"✅ Arbitraje: {len(result)} oportunidades encontradas")
    
    return result


def run_value_betting(snapshots: List[Snapshot]) -> List[Dict]:
    """
    Ejecutar detector de value betting sobre snapshots.
    
    Args:
        snapshots: Lista de Snapshots inmutables
    
    Returns:
        Lista de oportunidades de value betting
    """
    logger.info("💎 Ejecutando detector de value betting...")
    
    detector = ValueBetDetector()
    opportunities = detector.detect_value_bets(snapshots)  # ✅ CORREGIDO
    
    result = [opp.to_dict() for opp in opportunities]
    
    # Filtrar por probabilidad mínima
    min_prob = config.get("thresholds", {}).get("min_value_probability", 0.65)
    result = [o for o in result if o.get("value_probability", 0) >= min_prob]
    
    logger.info(f"✅ Value Betting: {len(result)} oportunidades encontradas")
    
    return result

def run_dutching(snapshots: List[Snapshot]) -> List[Dict]:
    """
    Ejecutar calculador de Dutching sobre snapshots.
    
    Args:
        snapshots: Lista de Snapshots inmutables
    
    Returns:
        Lista de oportunidades de Dutching (diccionarios)
    """
    logger.info("📊 Ejecutando calculador de dutching...")
    
    # Configuración desde config.yaml
    dutching_config = config.get("dutching", {})
    total_stake = dutching_config.get("total_stake", 100.0)
    min_profit_margin = dutching_config.get("min_profit_margin", 0.0) / 100.0  # Convertir %
    
    calculator = DutchingCalculator(
        total_stake=total_stake,
        min_profit_margin=min_profit_margin
    )
    
    # Detectar oportunidades de Dutching
    opportunities = calculator.detect_opportunities(snapshots)
    
    # Convertir a dict
    result = [opp.to_dict() for opp in opportunities]
    
    logger.info(f"✅ Dutching: {len(result)} oportunidades encontradas")
    
    return result

def run_pipeline(
    source: str = "csv",
    mode: str = "all",
    save: bool = True,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Ejecutar pipeline completo
    
    Args:
        source: Fuente de datos (csv | web)
        mode: Modo de ejecución (all | arbitrage | value | dutching)
        save: Guardar resultados en BD
        limit: Límite de snapshots a procesar
    
    Returns:
        Diccionario con resultados
    """
    logger.info(f"🚀 Iniciando pipeline con fuente: {source}, modo: {mode}")
    
    # 1. Obtener datos (Snapshots inmutables) - Principio #2
    provider = ConnectorFactory.create(source, config)  # ✅ CORREGIDO
    snapshots = provider.fetch_snapshots()
    
    if not snapshots:
        logger.error("❌ No se obtuvieron snapshots")
        return {"error": "No se obtuvieron snapshots"}
    
    if limit:
        snapshots = snapshots[:limit]
    
    logger.info(f"📥 Obtenidos {len(snapshots)} snapshots")
    
    # 2. Ejecutar estrategias
    strategies = config.get("strategies", {})
    all_opportunities = []
    results = {}
    
    if mode in ["all", "arbitrage"] and strategies.get("arbitrage", False):
        opps = run_arbitrage(snapshots)
        all_opportunities.extend(opps)
        results["arbitrage"] = len(opps)
    
    if mode in ["all", "value"] and strategies.get("value_betting", False):
        opps = run_value_betting(snapshots)
        all_opportunities.extend(opps)
        results["value_betting"] = len(opps)
    
    if mode in ["all", "dutching"] and strategies.get("dutching", False):
        opps = run_dutching(snapshots)
        all_opportunities.extend(opps)
        results["dutching"] = len(opps)
    
    # 3. Guardar en base de datos (Principio #3)
    if save and all_opportunities:
        repo = Repository()
        events = [s.to_dict() for s in snapshots]
        snapshot_id = repo.save_snapshot(events, source)
        repo.save_opportunities(all_opportunities, snapshot_id)
        logger.info(f"💾 Guardados {len(all_opportunities)} oportunidades en BD")
        results["snapshot_id"] = snapshot_id
    
    results["total_opportunities"] = len(all_opportunities)
    results["events_processed"] = len(snapshots)
    results["opportunities"] = all_opportunities
    
    # 4. Mostrar resumen
    print_summary(results)
    
    return results


def print_summary(results: Dict[str, Any]):
    """Imprimir resumen de resultados"""
    print("\n" + "="*60)
    print("📊 RESUMEN DE EJECUCIÓN")
    print("="*60)
    print(f"📥 Snapshots procesados: {results.get('events_processed', 0)}")
    print(f"🎯 Total oportunidades: {results.get('total_opportunities', 0)}")
    
    if "arbitrage" in results:
        print(f"   🔄 Arbitraje: {results['arbitrage']}")
    if "value_betting" in results:
        print(f"   💎 Value Betting: {results['value_betting']}")
    if "dutching" in results:
        print(f"   📊 Dutching: {results['dutching']}")
    
    if results.get("snapshot_id"):
        print(f"💾 Snapshot ID: {results['snapshot_id']}")
    
    # Mostrar top oportunidades
    opportunities = results.get("opportunities", [])
    if opportunities:
        print("\n🏆 TOP 5 OPORTUNIDADES:")
        print("-"*60)
        for i, opp in enumerate(opportunities[:5], 1):
            strategy = opp.get("strategy", "N/A")
            event = opp.get("event", "Desconocido")
            profit = opp.get("profit_percent", 0)
            print(f"{i}. [{strategy.upper()}] {event}")
            print(f"   💰 Beneficio: {profit:.2f}%")
            print("-"*40)
    
    print("="*60)


def show_stats():
    """Mostrar estadísticas de la base de datos"""
    logger.info("📊 Obteniendo estadísticas...")
    
    repo = Repository()
    stats = repo.get_stats()
    
    print("\n" + "="*50)
    print("📊 ESTADÍSTICAS DEL SISTEMA")
    print("="*50)
    print(f"📥 Total snapshots: {stats.get('total_snapshots', 0)}")
    print(f"🎯 Total oportunidades: {stats.get('total_opportunities', 0)}")
    print(f"📈 Arbitraje: {stats.get('arbitrage_count', 0)}")
    print(f"💎 Value Betting: {stats.get('value_betting_count', 0)}")
    print(f"📊 Dutching: {stats.get('dutching_count', 0)}")
    print(f"💾 Tamaño BD: {stats.get('db_size_mb', 0):.2f} MB")
    print(f"📅 Última ejecución: {stats.get('last_execution', 'N/A')}")
    print("="*50)
    
    return stats


def cleanup_database(days: int):
    """
    Limpiar datos antiguos
    
    Args:
        days: Días a conservar
    """
    logger.info(f"🧹 Limpiando datos anteriores a {days} días...")
    
    repo = Repository()
    deleted = repo.cleanup_old_data(days)
    
    print(f"✅ Eliminados {deleted} registros antiguos")
    
    return deleted


def export_results(
    output_file: str,
    format: str = "json",
    days: int = 7
):
    """
    Exportar resultados a archivo
    
    Args:
        output_file: Ruta del archivo de salida
        format: Formato (json | csv)
        days: Días a exportar
    """
    logger.info(f"📤 Exportando resultados a {output_file} ({format})")
    
    repo = Repository()
    cutoff_date = datetime.now() - timedelta(days=days)
    opportunities = repo.get_opportunities_since(cutoff_date)
    
    if not opportunities:
        print("❌ No hay oportunidades para exportar")
        return
    
    # Crear directorio si no existe
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    if format == "json":
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(opportunities, f, indent=2, ensure_ascii=False, default=str)
    elif format == "csv":
        if opportunities:
            keys = opportunities[0].keys()
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(opportunities)
    else:
        print(f"❌ Formato no soportado: {format}")
        return
    
    print(f"✅ Exportadas {len(opportunities)} oportunidades a {output_file}")


def generate_report(days: int = 7) -> Dict[str, Any]:
    """
    Generar reporte detallado
    
    Args:
        days: Días a incluir en el reporte
    
    Returns:
        Diccionario con reporte
    """
    logger.info(f"📋 Generando reporte de {days} días...")
    
    repo = Repository()
    cutoff_date = datetime.now() - timedelta(days=days)
    opportunities = repo.get_opportunities_since(cutoff_date)
    
    # Estadísticas por estrategia
    strategies = {}
    total_profit = 0.0
    
    for opp in opportunities:
        strategy = opp.get("strategy", "unknown")
        if strategy not in strategies:
            strategies[strategy] = {
                "count": 0,
                "total_profit": 0.0,
                "avg_profit": 0.0,
                "max_profit": 0.0
            }
        
        profit = opp.get("profit_percent", 0)
        strategies[strategy]["count"] += 1
        strategies[strategy]["total_profit"] += profit
        if profit > strategies[strategy]["max_profit"]:
            strategies[strategy]["max_profit"] = profit
        
        total_profit += profit
    
    # Calcular promedios
    for strategy in strategies.values():
        if strategy["count"] > 0:
            strategy["avg_profit"] = strategy["total_profit"] / strategy["count"]
    
    # Top eventos
    top_events = sorted(
        opportunities,
        key=lambda x: x.get("profit_percent", 0),
        reverse=True
    )[:10]
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "period_days": days,
        "total_opportunities": len(opportunities),
        "total_profit_avg": total_profit / len(opportunities) if opportunities else 0,
        "strategies": strategies,
        "top_events": top_events,
        "by_sport": {},
        "by_market": {}
    }
    
    # Agrupar por deporte
    for opp in opportunities:
        sport = opp.get("sport", "unknown")
        if sport not in report["by_sport"]:
            report["by_sport"][sport] = 0
        report["by_sport"][sport] += 1
    
    # Agrupar por mercado
    for opp in opportunities:
        market = opp.get("market_type", "unknown")
        if market not in report["by_market"]:
            report["by_market"][market] = 0
        report["by_market"][market] += 1
    
    # Mostrar reporte
    print("\n" + "="*60)
    print("📋 REPORTE DE OPORTUNIDADES")
    print("="*60)
    print(f"📅 Período: {days} días")
    print(f"🎯 Total oportunidades: {report['total_opportunities']}")
    print(f"💰 Beneficio promedio: {report['total_profit_avg']:.2f}%")
    print("\n📊 Por estrategia:")
    for strategy, data in strategies.items():
        print(f"   {strategy}: {data['count']} oportunidades, {data['avg_profit']:.2f}% promedio")
    print("\n🏆 Top eventos:")
    for i, event in enumerate(top_events[:5], 1):
        print(f"   {i}. {event.get('event', 'N/A')} - {event.get('profit_percent', 0):.2f}%")
    print("="*60)
    
    return report


def main():
    """Punto de entrada principal"""
    parser = argparse.ArgumentParser(
        description="QuantBet - Sistema de Arbitraje Deportivo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py --mode all --source csv
  python main.py --mode arbitrage --source web
  python main.py --serve
  python main.py --stats
  python main.py --cleanup 30
  python main.py --export results.json
  python main.py --report 7
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["all", "arbitrage", "value", "dutching"],
        default="all",
        help="Modo de ejecución (default: all)"
    )
    
    parser.add_argument(
        "--source",
        choices=["csv", "web", "oddsapi"],
        default="csv",
        help="Fuente de datos (default: csv)"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        metavar="N",
        help="Límite de snapshots a procesar"
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="No guardar resultados en BD"
    )
    
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Iniciar dashboard web"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Mostrar estadísticas de la base de datos"
    )
    
    parser.add_argument(
        "--cleanup",
        type=int,
        metavar="DAYS",
        help="Limpiar datos antiguos (días)"
    )
    
    parser.add_argument(
        "--export",
        metavar="FILE",
        help="Exportar resultados a archivo (JSON o CSV)"
    )
    
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Formato de exportación (default: json)"
    )
    
    parser.add_argument(
        "--report",
        type=int,
        metavar="DAYS",
        nargs="?",
        const=7,
        help="Generar reporte de N días (default: 7)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Activar modo debug"
    )
    
    args = parser.parse_args()
    
    # Configurar debug
    if args.debug:
        config["logs"]["level"] = "DEBUG"
        logger.setLevel("DEBUG")
        logger.debug("🔍 Modo debug activado")
    
    # --- Comandos de gestión ---
    
    if args.serve:
        # Iniciar servidor web
        logger.info("🌐 Iniciando dashboard web...")
        try:
            from src.web.app import create_app
            web_config = config.get("web", {})
            app = create_app()
            app.run(
                host=web_config.get("host", "0.0.0.0"),
                port=web_config.get("port", 5000),
                debug=web_config.get("debug", False) or args.debug
            )
        except ImportError as e:
            logger.error(f"❌ Error importando módulo web: {e}")
            sys.exit(1)
        return
    
    if args.stats:
        show_stats()
        return
    
    if args.cleanup:
        cleanup_database(args.cleanup)
        return
    
    if args.export:
        export_results(args.export, args.format)
        return
    
    if args.report:
        generate_report(args.report)
        return
    
    # --- Ejecución principal ---
    
    try:
        results = run_pipeline(
            source=args.source,
            mode=args.mode,
            save=not args.no_save,
            limit=args.limit
        )
        
        if results.get("error"):
            sys.exit(1)
        
        # Si hay oportunidades y se guardaron, mostrar estadísticas
        if results.get("total_opportunities", 0) > 0 and not args.no_save:
            print("\n💡 Ejecuta 'python main.py --stats' para ver estadísticas completas")
        
    except KeyboardInterrupt:
        logger.info("⏹️ Ejecución interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()