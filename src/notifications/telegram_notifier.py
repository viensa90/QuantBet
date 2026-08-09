import requests
from src.config_loader import ConfigLoader
from src.logger import log

BOOKMAKER_EMOJI = {
    'pinnacle': '🟠',
    'onexbet': '🔵',
    'betonlineag': '🔴',
    'betfair': '🟡',
}
FALLBACK_EMOJI = '⚪'


def _format_opportunity(opp) -> str:
    lines = [f"⚽ *{opp.event_name}*"]
    lines.append(f"   Mercado {opp.market} | Profit *{opp.profit_percent:.2f}%*")
    stakes, retorno = opp._calculate_stakes(100.0)
    for i, outcome in enumerate(opp.outcomes):
        bookmaker, name, price = opp._parse_outcome(outcome)
        stake = stakes[i]
        emoji = BOOKMAKER_EMOJI.get(bookmaker.lower(), FALLBACK_EMOJI)
        lines.append(f"   {emoji} {name} @{price:.2f} \\({bookmaker}\\) → ${stake:.2f}")
    lines.append(f"   💰 Inv: $100.00 | Ret: ${retorno:.2f} | Gan: ${retorno - 100:.2f}")
    return "\n".join(lines)


def maybe_notify(opportunities):
    cfg = ConfigLoader()
    token = cfg.telegram_token
    chat_id = cfg.telegram_chat_id
    if not token or not chat_id:
        log.warning("Telegram no configurado – no se enviarán notificaciones.")
        return

    if not opportunities:
        log.info("Sin oportunidades, no se envía notificación.")
        return

    header = f"🚀 *QuantBet – {len(opportunities)} oportunidad(es) de arbitraje*"
    parts = [header]
    for opp in opportunities[:10]:
        parts.append(_format_opportunity(opp))
    message = "\n\n".join(parts)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        log.info("Notificación de Telegram enviada correctamente.")
    except Exception as e:
        log.error(f"Error al enviar notificación Telegram: {e}")