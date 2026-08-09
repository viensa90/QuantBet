#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QuantBet - Sistema de Arbitraje Deportivo Automatizado
Versión: 0.5.0
"""

import argparse
import sys
from datetime import datetime

from src.config_loader import config, get_api_key   # <-- CORREGIDO: importamos config directamente
from src.logger import setup_logger, log
from src.connectors.factory import get_provider
from src.core.arbitrage import ArbitrageEngine
from src.storage.database import init_db
from src.storage.repository import OpportunityRepository
from src.notifications.telegram_notifier import maybe_notify


def banner():
    print("""
 ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗████████╗██████╗ ███████╗████████╗
██╔═══██╗██║   ██║██╔══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔════╝╚══██╔══╝
██║   ██║██║   ██║███████║██╔██╗ ██║   ██║   ██████╔╝█████╗     ██║
██║▄▄ ██║██║   ██║██╔══██║██║╚██╗██║   ██║   ██╔══██╗██╔══╝     ██║
╚██████╔╝╚██████╔╝██║  ██║██║ ╚████║   ██║   ██████╔╝███████╗   ██║
 ╚══▀▀═╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═════╝ ╚══════╝   ╚═╝
    """)
    print("QuantBet - Arbitraje Deportivo Automatizado")
    print("=" * 60)
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()


def main():
    parser = argparse.ArgumentParser(description="QuantBet - Arbitraje Deportivo Automatizado")
    parser.add_argument("--simple", action="store_true", help="Salida simplificada (sin arte ASCII)")
    parser.add_argument("--no-save", action="store_true", help="No persistir en BD")
    parser.add_argument("--sports", type=str, help="Filtrar deportes (separados por coma)")
    parser.add_argument("--markets", type=str, help="Filtrar mercados (separados por coma)")
    parser.add_argument("--min-profit", type=float, help="Umbral de profit mínimo (%)")
    args = parser.parse_args()

    # Configurar logger
    setup_logger()

    # Banner
    if not args.simple:
        banner()
    else:
        log.info("QuantBet v0.5.0 iniciado en modo simple")

    # Cargar configuración (ya está cargada al importar config, pero permitimos sobrescribir con args)
    # Usamos una copia para no modificar el original
    cfg = config.copy() if isinstance(config, dict) else config

    # Sobrescribir config con argumentos de línea de comandos
    if args.sports:
        cfg['sports'] = [s.strip() for s in args.sports.split(",")]
    if args.markets:
        cfg['markets'] = args.markets
    if args.min_profit:
        cfg['min_profit_percent'] = args.min_profit

    log.info(f"Deportes: {', '.join(cfg['sports'])}")
    log.info(f"Mercados: {cfg['markets']}")
    log.info(f"Profit mínimo: {cfg['min_profit_percent']}%")
    log.info(f"Bookmakers permitidos: {', '.join(cfg.get('allowed_bookmakers', []))}")

    # Inicializar proveedor de datos
    provider = get_provider()

    # Inicializar base de datos (WAL activado)
    init_db()

    # Inicializar repositorio y motor de arbitraje
    repo = OpportunityRepository()
    engine = ArbitrageEngine()

    all_opportunities = []
    total_events = 0
    total_snapshots = 0

    # Pipeline principal
    for sport_key in cfg['sports']:
        log.info(f"Procesando {sport_key}...")
        outcomes = provider.fetch(sport_key, markets=cfg['markets'])
        
        if not outcomes:
            log.warning(f"Sin datos para {sport_key}")
            continue
        
        total_events += len(set(o.event_name for o in outcomes))
        total_snapshots += len(outcomes)
        
        # Buscar oportunidades de arbitraje
        opportunities = engine.find_opportunities(
            outcomes,
            min_profit=cfg['min_profit_percent'] / 100
        )
        
        if opportunities:
            log.info(f"  -> {len(opportunities)} oportunidades en {sport_key}")
            all_opportunities.extend(opportunities)

    # Mostrar resultados
    print()
    log.info(f"Resumen: {total_events} eventos, {total_snapshots} snapshots, {len(all_opportunities)} oportunidades")
    print()

    if all_opportunities:
        print("=" * 60)
        print(f"   🚀 OPORTUNIDADES DE ARBITRAJE ENCONTRADAS: {len(all_opportunities)}")
        print("=" * 60)
        print()
        
        for i, opp in enumerate(all_opportunities, 1):
            print(f"--- Oportunidad #{i} ---")
            if args.simple:
                print(opp.summary())
            else:
                print(opp.detail())
            print()

        # Guardar en BD
        if not args.no_save:
            saved = repo.save_batch(all_opportunities)
            log.info(f"{saved} oportunidades guardadas en BD.")

        # Notificar por Telegram
        maybe_notify(all_opportunities)
    else:
        print("😔 No se encontraron oportunidades de arbitraje.")
        print("   Posibles causas:")
        print("   - Mercados muy eficientes en este momento")
        print("   - Umbral de profit demasiado alto")
        print("   - Bookmakers limitados en el plan gratuito")
        print()
        log.info("Sin oportunidades. Revisa los filtros o espera a mejores cuotas.")

    print(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("Pipeline finalizado.")


if __name__ == "__main__":
    main()