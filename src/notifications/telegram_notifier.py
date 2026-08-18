import requests
from datetime import datetime
from collections import defaultdict
from src.config_loader import ConfigLoader
from src.logger import get_logger

logger = get_logger(__name__)

# ------------------------------------------------------------
# Mapeos de nombres legibles y emojis
# ------------------------------------------------------------
DEPORTE_EMOJI = {
    'soccer': '⚽',
    'basketball': '🏀',
    'tennis': '🎾',
}
DEPORTE_NOMBRE = {
    'soccer': 'FÚTBOL',
    'basketball': 'BALONCESTO',
    'tenis': 'TENIS',
    'tennis': 'TENIS',   # por si acaso
}

LIGA_NOMBRE = {
    'soccer_epl': '🏴 Premier League',
    'soccer_spain_la_liga': '🇪🇸 La Liga',
    'soccer_italy_serie_a': '🇮🇹 Serie A',
    'soccer_italy_serie_b': '🇮🇹 Serie B',
    'soccer_germany_bundesliga': '🇩🇪 Bundesliga',
    'soccer_germany_bundesliga2': '🇩🇪 Bundesliga 2',
    'soccer_germany_dfb_pokal': '🇩🇪 DFB-Pokal',
    'soccer_germany_liga3': '🇩🇪 3. Liga',
    'soccer_france_ligue_one': '🇫🇷 Ligue 1',
    'soccer_france_ligue_two': '🇫🇷 Ligue 2',
    'soccer_netherlands_eredivisie': '🇳🇱 Eredivisie',
    'soccer_portugal_primeira_liga': '🇵🇹 Primeira Liga',
    'soccer_brazil_campeonato': '🇧🇷 Brasileirão',
    'soccer_brazil_serie_b': '🇧🇷 Brasileirão Série B',
    'soccer_argentina_primera_division': '🇦🇷 Primera Argentina',
    'soccer_usa_mls': '🇺🇸 MLS',
    'soccer_mexico_ligamx': '🇲🇽 Liga MX',
    'soccer_chile_campeonato': '🇨🇱 Campeonato Chileno',
    'soccer_china_superleague': '🇨🇳 Superliga China',
    'soccer_concacaf_leagues_cup': '🌎 Leagues Cup',
    'soccer_conmebol_copa_libertadores': '🌎 Copa Libertadores',
    'soccer_conmebol_copa_sudamericana': '🌎 Copa Sudamericana',
    'soccer_denmark_superliga': '🇩🇰 Superliga Danesa',
    'soccer_efl_champ': '🏴 Championship',
    'soccer_england_league1': '🏴 League One',
    'soccer_england_league2': '🏴 League Two',
    'soccer_finland_veikkausliiga': '🇫🇮 Veikkausliiga',
    'soccer_greece_super_league': '🇬🇷 Superliga Griega',
    'soccer_japan_j_league': '🇯🇵 J1 League',
    'soccer_korea_kleague1': '🇰🇷 K League 1',
    'soccer_norway_eliteserien': '🇳🇴 Eliteserien',
    'soccer_poland_ekstraklasa': '🇵🇱 Ekstraklasa',
    'soccer_russia_premier_league': '🇷🇺 Premier Rusa',
    'soccer_spain_segunda_division': '🇪🇸 La Liga 2',
    'soccer_sweden_allsvenskan': '🇸🇪 Allsvenskan',
    'soccer_sweden_superettan': '🇸🇪 Superettan',
    'soccer_turkey_super_league': '🇹🇷 Süper Lig',
    'soccer_uefa_champs_league_qualification': '🇪🇺 Champions League (Clasificación)',
    'soccer_uefa_nations_league': '🇪🇺 Nations League',
    'soccer_austria_bundesliga': '🇦🇹 Bundesliga Austríaca',
    'soccer_belgium_first_div': '🇧🇪 Pro League Belga',
    'basketball_nba': '🇺🇸 NBA',
    'basketball_wnba': '🇺🇸 WNBA',
    'tennis_atp_cincinnati_open': '🇺🇸 ATP Cincinnati',
    'tennis_wta_cincinnati_open': '🇺🇸 WTA Cincinnati',
}

BOOKMAKER_EMOJI = {
    'pinnacle': '🟠',
    '1xbet': '🔵',
    'betonline.ag': '🔴',
    'betfair': '🟡',
    'marathonbet': '🟢',
    'marathon bet': '🟢',  # por si aparece con espacio
}
FALLBACK_EMOJI = '⚪'

MARKET_NOMBRE = {
    'h2h': '1X2',
    'totals': 'Over/Under',
    'spreads': 'Hándicap',
}

# ------------------------------------------------------------
# Funciones auxiliares
# ------------------------------------------------------------
def _format_event_time(event_time):
    if not event_time:
        return 'Fecha desconocida'
    try:
        dt = datetime.fromisoformat(event_time.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y %H:%M')
    except:
        return event_time

def _format_market(market):
    return MARKET_NOMBRE.get(market, market)

def _get_sport_from_sport_key(sport):
    if sport.startswith('soccer'):
        return 'soccer'
    elif sport.startswith('basketball'):
        return 'basketball'
    elif sport.startswith('tennis'):
        return 'tennis'
    return sport

def _order_outcomes(outcomes):
    """Ordena las patas: si hay DRAW lo coloca en el medio; resto alfabético."""
    if len(outcomes) == 3:
        # detectar draw/empate
        draw_idx = None
        for i, o in enumerate(outcomes):
            name = o['outcome'].lower()
            if name in ['draw', 'empate', 'x']:
                draw_idx = i
                break
        if draw_idx is not None:
            others = [o for j, o in enumerate(outcomes) if j != draw_idx]
            others_sorted = sorted(others, key=lambda x: x['outcome'])
            draw = outcomes[draw_idx]
            return [others_sorted[0], draw, others_sorted[1]]
    # fallback: orden alfabético
    return sorted(outcomes, key=lambda x: x['outcome'])

def _format_opportunity(opp, sport_emoji):
    lines = []
    market = _format_market(opp.market)
    event_time = _format_event_time(opp.event_time)
    live_info = ''
    if getattr(opp, 'is_live', False):
        live_info = ' 🔴 EN VIVO'
    lines.append(f"{sport_emoji} *{opp.event_name}*")
    lines.append(f"   Mercado: {market} | Profit: *{opp.profit_percent:.2f}%*")
    lines.append(f"   🕒 {event_time}{live_info}")
    outcomes = _order_outcomes(opp.details['outcomes'])
    for outcome in outcomes:
        bookmaker = outcome['bookmaker']
        emoji = BOOKMAKER_EMOJI.get(bookmaker.lower(), FALLBACK_EMOJI)
        stake = outcome['stake']
        odds = outcome['odds']
        name = outcome['outcome']
        lines.append(f"   {emoji} ({bookmaker}) @ {odds} → {name} → {stake:.2f} $")
    total = opp.details['total_investment']
    retorno = opp.details['guaranteed_return']
    ganancia = opp.profit
    lines.append(f"   💰 Inv: {total:.2f} $ | Ret: {retorno:.2f} $ | Gan: {ganancia:.2f} $")
    return "\n".join(lines)

def maybe_notify(opportunities):
    cfg = ConfigLoader()
    token = cfg.telegram_token
    chat_id = cfg.telegram_chat_id
    if not token or not chat_id:
        logger.warning("Telegram no configurado – no se enviarán notificaciones.")
        return

    if not opportunities:
        logger.info("Sin oportunidades, no se envía notificación.")
        return

    # Agrupar por deporte y liga
    grouped = defaultdict(lambda: defaultdict(list))
    for opp in opportunities[:50]:   # límite 50
        sport = _get_sport_from_sport_key(opp.sport)
        liga = opp.sport
        grouped[sport][liga].append(opp)

    header = f"🚀 *QuantBet – {len(opportunities)} oportunidad(es) de arbitraje*"
    parts = [header]

    # Recorrer deportes y ligas
    for sport, ligas in grouped.items():
        sport_emoji = DEPORTE_EMOJI.get(sport, '🏅')
        sport_name = DEPORTE_NOMBRE.get(sport, sport.upper())
        parts.append(f"\n{sport_emoji} *{sport_name}*")
        for liga_slug, opps in ligas.items():
            liga_label = LIGA_NOMBRE.get(liga_slug, liga_slug)
            parts.append(f"   {liga_label}")
            for opp in opps:
                parts.append(_format_opportunity(opp, sport_emoji))
                parts.append("")  # línea en blanco entre oportunidades

    message = "\n".join(parts)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Notificación de Telegram enviada correctamente.")
    except Exception as e:
        logger.error(f"Error al enviar notificación Telegram: {e}")