"""Utility functions for RSI calculations."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, List

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


def format_rsi_message(extreme_rsi: Dict[str, str]) -> Tuple[str, str]:
    """Format extreme RSI readings into a rich Markdown message."""
    if not extreme_rsi:
        return "", ""

    overbought_items: List[Tuple[str, str]] = []
    oversold_items: List[Tuple[str, str]] = []

    for indicator, status in extreme_rsi.items():
        if "超买" in status:
            rsi_value = status.split(': ')[1]
            overbought_items.append((indicator, rsi_value))
        elif "超卖" in status:
            rsi_value = status.split(': ')[1]
            oversold_items.append((indicator, rsi_value))

    title = f"RSI-{len(overbought_items)}个超买,{len(oversold_items)}个超卖信号"

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
            "| 加密货币 | RSI指标 | RSI值 |",
            "|---------|--------|-------|",
        ])
        for indicator, rsi_value in overbought_items:
            parts = indicator.split(' (')
            crypto_name = parts[0]
            rsi_type = parts[1].rstrip(')')
            content_lines.append(
                f"| **{crypto_name}** | `{rsi_type}` | **{rsi_value}** |",
            )
        content_lines.extend(["", "> 📉 **建议**: 考虑卖出，获利了结", ""])

    if oversold_items:
        content_lines.extend([
            "### 🟢 **超卖区域** `买入信号`",
            "",
            "| 加密货币 | RSI指标 | RSI值 |",
            "|---------|--------|-------|",
        ])
        for indicator, rsi_value in oversold_items:
            parts = indicator.split(' (')
            crypto_name = parts[0]
            rsi_type = parts[1].rstrip(')')
            content_lines.append(
                f"| **{crypto_name}** | `{rsi_type}` | **{rsi_value}** |",
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
