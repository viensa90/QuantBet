"""
Motor de arbitraje para QuantBet.
Detecta oportunidades de arbitraje comparando cuotas entre bookmakers.
"""
import logging
from typing import List, Dict, Optional, Tuple
from itertools import combinations

from src.domain.entities import Snapshot, Opportunity
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Mapeo de selecciones opuestas por tipo de mercado
OPPOSITE_MAP = {
    "1X2": {"home": "away", "away": "home", "draw": "draw"},
    "Tennis Winner": {"home": "away", "away": "home"},
    "Basketball Moneyline": {"home": "away", "away": "home"},
}

# Mercados que funcionan con lógica over/under (prefijo "over_" / "under_")
OVER_UNDER_MARKETS = {
    "Over/Under", "Tennis Total Games", "Basketball Total Points",
    "Asian Handicap", "Tennis Set Handicap", "Basketball Spread"
}


class ArbitrageEngine:
    """Motor principal de detección de arbitraje."""

    def __init__(self, min_profit_percent: float = 0.0):
        self.min_profit = min_profit_percent / 100.0

    def detect_opportunities(self, snapshots: List[Snapshot]) -> List[Opportunity]:
        groups: Dict[Tuple[str, str], List[Snapshot]] = {}
        for snap in snapshots:
            key = (snap.event_id, snap.market_type)
            groups.setdefault(key, []).append(snap)

        all_opps = []
        for (event_id, market_type), group in groups.items():
            if len(group) < 2:
                continue
            opps = self._find_arbitrage_opportunities(group, market_type)
            all_opps.extend(opps)

        logger.info("Total oportunidades detectadas: %d", len(all_opps))
        return all_opps

    def _find_arbitrage_opportunities(
        self, snapshots: List[Snapshot], market_type: str
    ) -> List[Opportunity]:
        opportunities = []
        for snap1, snap2 in combinations(snapshots, 2):
            if snap1.bookmaker == snap2.bookmaker:
                continue
            odds1 = snap1.odds_data
            odds2 = snap2.odds_data

            for sel in odds1:
                opposite = self._get_opposite_selection(sel, market_type)
                if not opposite or opposite not in odds2:
                    continue
                margin = 1.0 / odds1[sel] + 1.0 / odds2[opposite]
                if margin < 1.0:
                    profit_percent = (1.0 - margin) * 100
                    if profit_percent >= self.min_profit * 100:
                        stakes = self._calculate_stakes(odds1[sel], odds2[opposite])
                        opp = Opportunity(
                            event_id=snap1.event_id,
                            market_type=market_type,
                            profit_percent=round(profit_percent, 2),
                            odds={
                                snap1.bookmaker: {sel: odds1[sel]},
                                snap2.bookmaker: {opposite: odds2[opposite]}
                            },
                            stakes=stakes,
                            source=f"{snap1.bookmaker} vs {snap2.bookmaker}",
                            timestamp=datetime.now(timezone.utc)
                        )
                        opportunities.append(opp)
        return opportunities

    def _get_opposite_selection(self, selection: str, market_type: str) -> Optional[str]:
        if market_type in OVER_UNDER_MARKETS:
            if selection.startswith("over"):
                return selection.replace("over", "under", 1)
            elif selection.startswith("under"):
                return selection.replace("under", "over", 1)
            return None
        mapping = OPPOSITE_MAP.get(market_type, {})
        return mapping.get(selection)

    def _calculate_stakes(self, odd1: float, odd2: float, total: float = 100.0) -> Dict[str, float]:
        stake1 = total / (1 + odd1 / odd2)
        stake2 = total - stake1
        return {"stake_selection1": round(stake1, 2), "stake_selection2": round(stake2, 2)}