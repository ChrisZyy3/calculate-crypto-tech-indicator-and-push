"""Utility functions for RSI calculations."""

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd

from config import shared


def calculate_rsi(prices: pd.Series, period: int = 14) -> Optional[pd.Series]:
    """Calculate RSI values using exponential moving averages.

    Args:
        prices: Series of prices.
        period: Number of periods for RSI calculation.

    Returns:
        Series of RSI values or None if insufficient data.
    """
    if prices is None or len(prices) < period + 1:
        return None

    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def analyze_extreme_rsi(results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    """Find overbought and oversold RSI readings."""
    extreme: Dict[str, str] = {}
    for symbol, data in results.items():
        if data.get("error"):
            continue

        r14 = data.get("rsi_14")
        if isinstance(r14, float):
            if r14 >= shared.RSI_OVERBOUGHT_14:
                extreme[f"{symbol} (RSI-14)"] = f"超买: {r14:.2f}"
            elif r14 <= shared.RSI_OVERSOLD_14:
                extreme[f"{symbol} (RSI-14)"] = f"超卖: {r14:.2f}"

        r6 = data.get("rsi_6")
        if isinstance(r6, float):
            if r6 >= shared.RSI_OVERBOUGHT_6:
                extreme[f"{symbol} (RSI-6)"] = f"超买: {r6:.2f}"
            elif r6 <= shared.RSI_OVERSOLD_6:
                extreme[f"{symbol} (RSI-6)"] = f"超卖: {r6:.2f}"

    return extreme
