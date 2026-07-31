#!/usr/bin/env python3
"""
QuantBet - Sistema de Arbitraje Deportivo Automatizado
CLI principal con soporte multi-estrategia, multi-conector y dashboard web.
"""

import argparse
import sys
from typing import Optional

from src.config_loader import ConfigLoader
from src.logger import setup_logging, get_logger
from src.storage.database import Database
from src.storage.repository import Repository
from src.connectors.factory import ConnectorFactory
from src.core.arbitrage import ArbitrageEngine
from src.core.scorer import Scorer
from src.core.bankroll import BankrollManager
from src.core.value_betting import ValueBetDetector
from src.core.dutching import DutchingCalculator
from src.domain.entities import MarketType

logger = get_logger(__name__)


def parse_markets(markets_str: Optional[str]) -> list:
    """
    Parsea lista de mercados desde argumento CLI.
    
    Args:
        markets_str: String con mercados separados por coma
        
    Returns:
        Lista de MarketType
    """
    if not markets_str:
        return None
    
    market_map = {
        "1X2": MarketType.MERCADO_1X2,
        "OVER_UNDER": MarketType.OVER_UNDER,
        "ASIAN_HANDICAP": MarketType.ASIAN_HANDICAP,
        "DOUBLE_CHANCE": MarketType.DOUBLE_CHANCE,
    }
    
    markets = []
    for m in markets_str.split(','):
        m = m.strip().upper()
        if m in market_map:
            markets.append(market_map[m])
        else:
            logger.warning("Mercado no reconocido: %s", m)
    
    return markets if markets else None


def run_arbitrage(
    connector, 
    repository: Repository,
    bankroll: BankrollManager,
    config: dict,
    enabled_markets: Optional[list] = None
) -> None:
    """Ejecuta pipeline de arbitraje."""
    logger.info("=== EJECUTANDO ARBITRAJE ===")
    
    # 1. Obtener snapshots
    snapshots = connector.fetch_snapshots()
    logger.info("Snapshots obtenidos: %d", len(snapshots))
    
    if not snapshots:
        logger.warning("No hay snapshots para procesar")
        return
    
    # 2. Guardar snapshots
    for snapshot in snapshots:
        repository.save_snapshot(snapshot)
    logger.info("Snapshots guardados: %d", len(snapshots))
    
    # 3. Detectar oportunidades
    engine = ArbitrageEngine(enabled_markets=enabled_markets)
    opportunities = engine.detect_opportunities(snapshots)
    
    if not opportunities:
        logger.info("No se detectaron oportunidades de arbitraje")
        return
    
    logger.info("Oportunidades detectadas: %d", len(opportunities))
    
    # 4. Puntuación
    scorer = Scorer()
    threshold = config.get('decision', {}).get('min_arbitrage_percent', 2.0)
    scored_ops = scorer.score_opportunities(opportunities, threshold)
    
    scored_ops = [op for op in scored_ops if op.score >= threshold]
    logger.info("Oportunidades con score >= %s%%: %d", threshold, len(scored_ops))
    
    # 5. Validar bankroll
    for op in scored_ops:
        if bankroll.can_bet(op):
            logger.info("OPORTUNIDAD VALIDADA: %s | Mercado: %s | Score: %.2f%% | Stake sugerido: %.2f %s",
                       op.opportunity.event_id,
                       op.opportunity.market_type.value,
                       op.score, 
                       bankroll.calculate_stake(op) or 0,
                       config.get('bankroll', {}).get('currency', 'EUR'))
            
            # Guardar decisión
            repository.save_decision(
                op.opportunity.event_id,
                op.opportunity.source,
                "ARBITRAGE",
                True,
                op.score,
                bankroll.calculate_stake(op) or 0,
                {
                    "arbitrage_percent": op.opportunity.arbitrage_percent,
                    "market_type": op.opportunity.market_type.value,
                    "metadata": op.opportunity.metadata
                }
            )
        else:
            logger.debug("Oportunidad rechazada por bankroll: %s", op.opportunity.event_id)
    
    logger.info("=== ARBITRAJE COMPLETADO ===")


def run_value_betting(
    connector,
    repository: Repository,
    bankroll: BankrollManager,
    config: dict
) -> None:
    """Ejecuta pipeline de value betting."""
    logger.info("=== EJECUTANDO VALUE BETTING ===")
    
    snapshots = connector.fetch_snapshots()
    if not snapshots:
        logger.warning("No hay snapshots para procesar")
        return
    
    detector = ValueBetDetector(config.get('fair_probabilities', {}))
    value_bets = detector.detect_value_bets(snapshots, config.get('decision', {}).get('min_value_threshold', 0.05))
    
    if not value_bets:
        logger.info("No se detectaron value bets")
        return
    
    logger.info("Value bets detectados: %d", len(value_bets))
    
    for vb in value_bets:
        logger.info("VALUE BET: %s | Mercado: %s | Valor: %.2f%%",
                   vb.event_id, vb.market_type.value, vb.value_percent * 100)
        # Guardar decisión
        repository.save_decision(
            vb.event_id,
            vb.source,
            "VALUE_BET",
            True,
            vb.value_percent,
            bankroll.calculate_stake_for_value(vb, config.get('bankroll', {})),
            {
                "fair_probability": vb.fair_probability,
                "actual_odds": float(vb.actual_odds),
                "market_type": vb.market_type.value
            }
        )
    
    logger.info("=== VALUE BETTING COMPLETADO ===")


def run_dutching(
    connector,
    repository: Repository,
    bankroll: BankrollManager,
    config: dict
) -> None:
    """Ejecuta pipeline de dutching."""
    logger.info("=== EJECUTANDO DUTCHING ===")
    
    snapshots = connector.fetch_snapshots()
    if not snapshots:
        logger.warning("No hay snapshots para procesar")
        return
    
    calculator = DutchingCalculator()
    dutching_ops = calculator.calculate_dutching(snapshots)
    
    if not dutching_ops:
        logger.info("No se detectaron oportunidades de dutching")
        return
    
    logger.info("Oportunidades de dutching detectadas: %d", len(dutching_ops))
    
    # Procesar cada oportunidad de dutching
    for event_id, dutch in dutching_ops.items():
        logger.info("DUTCHING: %s | Cobertura: %.2f%% | Stake total: %.2f",
                   event_id, dutch.coverage_percent * 100, dutch.total_stake)
        
        # Guardar decisión
        repository.save_decision(
            event_id,
            "DUTCHING",
            "DUTCHING",
            True,
            dutch.coverage_percent,
            dutch.total_stake,
            {
                "stakes": dutch.stakes,
                "expected_profit": float(dutch.expected_profit),
                "market_type": dutch.market_type.value
            }
        )
    
    logger.info("=== DUTCHING COMPLETADO ===")


def run_all(connector, repository: Repository, bankroll: BankrollManager, config: dict, enabled_markets: Optional[list] = None) -> None:
    """Ejecuta todas las estrategias."""
    logger.info("=== EJECUTANDO TODAS LAS ESTRATEGIAS ===")
    run_arbitrage(connector, repository, bankroll, config, enabled_markets)
    run_value_betting(connector, repository, bankroll, config)
    run_dutching(connector, repository, bankroll, config)
    logger.info("=== TODAS LAS ESTRATEGIAS COMPLETADAS ===")


def serve_dashboard(config_path: str, host: str = "127.0.0.1", port: int = 5000) -> None:
    """
    Inicia el servidor web del dashboard.
    
    Args:
        config_path: Ruta al archivo de configuración
        host: Host donde escuchar
        port: Puerto donde escuchar
    """
    from src.web.app import create_app
    
    logger.info("Iniciando dashboard en http://%s:%d", host, port)
    app = create_app(config_path)
    app.run(host=host, port=port, debug=True)


def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="QuantBet - Sistema de Arbitraje Deportivo Automatizado"
    )
    parser.add_argument(
        "--mode",
        choices=["arbitrage", "value", "dutching", "all"],
        default="all",
        help="Estrategia a ejecutar (por defecto: all)"
    )
    parser.add_argument(
        "--source",
        choices=["csv", "web"],
        default=None,
        help="Fuente de datos (csv o web). Si no se especifica, usa config.yaml"
    )
    parser.add_argument(
        "--markets",
        help="Mercados a procesar (separados por coma). Ej: '1X2,OVER_UNDER'"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Ruta al archivo de configuración"
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Iniciar el dashboard web en lugar de ejecutar estrategias"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host para el dashboard (por defecto: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Puerto para el dashboard (por defecto: 5000)"
    )
    
    args = parser.parse_args()
    
    # Cargar configuración
    config_loader = ConfigLoader(args.config)
    config = config_loader.load()
    
    # Configurar logging
    setup_logging(config.get('logging', {}))
    logger.info("QuantBet v%s iniciado", config.get('version', '0.2.0'))
    
    # Modo dashboard
    if args.serve:
        serve_dashboard(args.config, args.host, args.port)
        return
    
    # Modo pipeline
    # Inicializar BD
    db = Database(config.get('database', {}).get('path', 'quantbet.db'))
    repository = Repository(db)
    
    # Inicializar bankroll
    bankroll_config = config.get('bankroll', {})
    bankroll = BankrollManager(bankroll_config.get('initial', 1000.0))
    
    # Crear conector
    if args.source:
        connector = ConnectorFactory.create(args.source, config)
    else:
        connector = ConnectorFactory.create_from_config(config)
    
    # Parsear mercados
    enabled_markets = parse_markets(args.markets)
    if not enabled_markets:
        # Usar configuración
        markets_config = config.get('markets', {})
        enabled_markets_list = markets_config.get('enabled', ['1X2'])
        enabled_markets = parse_markets(','.join(enabled_markets_list))
    
    try:
        # Ejecutar estrategia seleccionada
        mode_map = {
            "arbitrage": run_arbitrage,
            "value": run_value_betting,
            "dutching": run_dutching,
            "all": run_all
        }
        
        # Preparar kwargs
        kwargs = {
            "connector": connector,
            "repository": repository,
            "bankroll": bankroll,
            "config": config
        }
        
        if args.mode in ["arbitrage", "all"]:
            kwargs["enabled_markets"] = enabled_markets
        
        mode_map[args.mode](**kwargs)
        
        # Mostrar resumen
        print("\n" + "=" * 50)
        print(f"📊 RESUMEN DE EJECUCIÓN")
        print(f"Modo: {args.mode}")
        print(f"Fuente: {args.source or config.get('connector', {}).get('type', 'csv')}")
        print(f"Mercados: {', '.join([m.value for m in enabled_markets])}")
        print(f"Bankroll actual: {bankroll.get_balance():.2f} {bankroll.currency}")
        print("=" * 50 + "\n")
        
    except Exception as e:
        logger.error("Error en ejecución: %s", str(e), exc_info=True)
        sys.exit(1)
    finally:
        # Cerrar recursos
        if hasattr(connector, 'close'):
            connector.close()


if __name__ == "__main__":
    main()