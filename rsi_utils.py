"""Utility functions for RSI calculations."""

from __future__ import annotations

import numbers
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd

from config import shared
from datetime import datetime


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


def analyze_extreme_rsi(results: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find overbought and oversold RSI readings.

    Args:
        results: Mapping of trading symbol to calculated RSI data.

    Returns:
        A list of dictionaries describing extreme RSI observations. Each
        dictionary contains the trading symbol, RSI indicator type (``RSI-14``
        or ``RSI-6``), the detected signal (``"超买"``/``"超卖"``), the RSI value
        itself and the latest available price.
    """

    extreme: List[Dict[str, Any]] = []
    for symbol, data in results.items():
        if data.get("error"):
            continue

        price = data.get("price")

        r14 = data.get("rsi_14")
        if isinstance(r14, numbers.Real):
            if r14 >= shared.RSI_OVERBOUGHT_14:
                extreme.append(
                    {
                        "symbol": symbol,
                        "indicator": "RSI-14",
                        "signal": "超买",
                        "rsi_value": float(r14),
                        "price": price,
                    }
                )
            elif r14 <= shared.RSI_OVERSOLD_14:
                extreme.append(
                    {
                        "symbol": symbol,
                        "indicator": "RSI-14",
                        "signal": "超卖",
                        "rsi_value": float(r14),
                        "price": price,
                    }
                )

        r6 = data.get("rsi_6")
        if isinstance(r6, numbers.Real):
            if r6 >= shared.RSI_OVERBOUGHT_6:
                extreme.append(
                    {
                        "symbol": symbol,
                        "indicator": "RSI-6",
                        "signal": "超买",
                        "rsi_value": float(r6),
                        "price": price,
                    }
                )
            elif r6 <= shared.RSI_OVERSOLD_6:
                extreme.append(
                    {
                        "symbol": symbol,
                        "indicator": "RSI-6",
                        "signal": "超卖",
                        "rsi_value": float(r6),
                        "price": price,
                    }
                )

    return extreme


def _format_price(value: Any) -> str:
    """Format the latest price for display in Markdown tables."""
    if isinstance(value, numbers.Real):
        return f"${float(value):,.2f}"
    return "--"


def format_rsi_message(
    extreme_rsi: Sequence[Dict[str, Any]], timeframe_tag: Optional[str] = None
) -> Tuple[str, str]:
    """Format extreme RSI readings into a rich Markdown message.

    Args:
        extreme_rsi: Extreme RSI readings collected from calculations.
        timeframe_tag: Optional label describing the timeframe (e.g. ``"rsi1d"``
            or ``"rsi4h"``) to be prefixed to the notification title.
    """
    if not extreme_rsi:
        return "", ""

    overbought_items: List[Dict[str, Any]] = []
    oversold_items: List[Dict[str, Any]] = []

    for entry in extreme_rsi:
        signal = entry.get("signal")
        if signal == "超买":
            overbought_items.append(entry)
        elif signal == "超卖":
            oversold_items.append(entry)

    base_title = f"RSI-{len(overbought_items)}个超买,{len(oversold_items)}个超卖信号"
    title = f"{timeframe_tag} | {base_title}" if timeframe_tag else base_title

    content_lines: List[str] = [
        "## 📈 RSI技术指标分析",
        "",
        f"🕰️ **检测时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
    ]

    if overbought_items:
        content_lines.extend([
            "### 🔴 **超买区域** `卖出信号`",
            "",
            "| 加密货币 | RSI指标 | RSI值 | 最新价格 |",
            "|---------|--------|-------|-----------|",
        ])
        for item in overbought_items:
            crypto_name = item.get("symbol", "--")
            rsi_type = item.get("indicator", "--")
            rsi_value = item.get("rsi_value")
            price_text = _format_price(item.get("price"))
            rsi_display = f"{float(rsi_value):.2f}" if isinstance(rsi_value, numbers.Real) else "--"
            content_lines.append(
                f"| **{crypto_name}** | `{rsi_type}` | **{rsi_display}** | {price_text} |",
            )
        content_lines.extend(["", "> 📉 **建议**: 考虑卖出，获利了结", ""])

    if oversold_items:
        content_lines.extend([
            "### 🟢 **超卖区域** `买入信号`",
            "",
            "| 加密货币 | RSI指标 | RSI值 | 最新价格 |",
            "|---------|--------|-------|-----------|",
        ])
        for item in oversold_items:
            crypto_name = item.get("symbol", "--")
            rsi_type = item.get("indicator", "--")
            rsi_value = item.get("rsi_value")
            price_text = _format_price(item.get("price"))
            rsi_display = f"{float(rsi_value):.2f}" if isinstance(rsi_value, numbers.Real) else "--"
            content_lines.append(
                f"| **{crypto_name}** | `{rsi_type}` | **{rsi_display}** | {price_text} |",
            )
        content_lines.extend(["", "> 📈 **建议**: 考虑买入，可能将反弹", ""])

    content_lines.extend([
        "---",
        "",
        "### 📊 RSI指标说明",
        "",
        "- **RSI-14**: 14日相对强弱指数 (超买: ≥ 65, 超卖: ≤ 35)",
        "- **RSI-6**: 6日相对强弱指数 (超买: ≥ 70, 超卖: ≤ 30)",
        "",
        "> ⚠️ **免责声明**: 仅供参考，不构成投资建议，请理性投资。",
    ])

    content = "\n".join(content_lines)
    return title, content
