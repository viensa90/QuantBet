#!/usr/bin/env python
"""
QuantBet - Pipeline principal.
Modo --simple: muestra en consola las oportunidades encontradas.
"""
import os
import sys
import argparse
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from src.config_loader import load_config
from src.logger import logger
from src.connectors.odds_api_provider import OddsAPIProvider
from src.core.arbitrage import ArbitrageEngine
from src.storage.repository import OpportunityRepository
from src.notifications.telegram_notifier import TelegramNotifier

def main():
    parser = argparse.ArgumentParser(description="QuantBet - Pipeline de arbitraje")
    parser.add_argument("--simple", action="store_true", help="Salida simplificada en consola")
    args = parser.parse_args()

    # 1. Cargar configuración
    config = load_config()
    sports = config.get("sports", [])
    min_profit = config.get("arbitrage", {}).get("min_profit_percent", 1.5)
    bookmakers = config.get("odds_api", {}).get("bookmakers", "")
    markets = config.get("markets", "h2h,totals")
    regions = config.get("regions", "eu")

    api_key = os.getenv("ODDS_API_KEY")
    if not api_key:
        logger.error("Falta ODDS_API_KEY en .env")
        sys.exit(1)

    # 2. Conector (con filtro de bookmakers)
    provider = OddsAPIProvider(
        api_key=api_key,
        bookmakers=bookmakers,
        regions=regions,
        markets=markets
    )

    # 3. Motor de arbitraje
    engine = ArbitrageEngine(min_profit_percent=min_profit)

    # 4. Repositorio (persistencia)
    repo = OpportunityRepository()

    # 5. Notificador Telegram (si está configurado)
    telegram_enabled = config.get("notifications", {}).get("telegram", {}).get("enabled", False)
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    notifier = None
    if telegram_enabled and bot_token and chat_id:
        notifier = TelegramNotifier(bot_token=bot_token, chat_id=chat_id)
        logger.info("Notificaciones Telegram activadas")
    else:
        logger.info("Notificaciones Telegram desactivadas o sin configuración")

    # 6. Ejecutar pipeline para cada deporte
    total_opportunities = 0
    for sport in sports:
        logger.info("Procesando deporte: %s", sport)
        events = provider.fetch_events(sport)
        if not events:
            logger.warning("No se obtuvieron eventos para %s", sport)
            continue

        opportunities = engine.find_opportunities(events)
        if not opportunities:
            logger.info("No se encontraron oportunidades en %s", sport)
            continue

        # Guardar en BD
        for opp in opportunities:
            repo.save_opportunity(opp)
            total_opportunities += 1
            if args.simple:
                print(f"✅ {opp.event_name} | {opp.market} | {opp.combination} | "
                      f"Profit: {opp.profit_percent:.2f}% | Apuesta: {opp.bet_info}")

        logger.info("Oportunidades en %s: %d", sport, len(opportunities))

    # 7. Resumen y notificación
    logger.info("Pipeline finalizado. Total oportunidades: %d", total_opportunities)

    if notifier and total_opportunities > 0:
        # Construir mensaje resumen
        lines = []
        lines.append("📊 *QuantBet - Nuevas oportunidades detectadas*")
        lines.append(f"Total: {total_opportunities}")
        lines.append("")
        # Recuperar las últimas 5 para detalle
        last_opps = repo.get_recent(limit=5)
        for opp in last_opps:
            lines.append(f"• *{opp.event_name}*")
            lines.append(f"  Mercado: {opp.market}")
            lines.append(f"  Combinación: {opp.combination}")
            lines.append(f"  Profit: {opp.profit_percent:.2f}%")
            lines.append(f"  Apuesta: {opp.bet_info}")
            lines.append("")
        if total_opportunities > 5:
            lines.append(f"... y {total_opportunities - 5} más. Revisa el dashboard.")

        message = "\n".join(lines)
        notifier.send_message(message)

    elif notifier and total_opportunities == 0:
        notifier.send_message("🔍 *QuantBet* - No se encontraron oportunidades en esta ejecución.")

if __name__ == "__main__":
    main()