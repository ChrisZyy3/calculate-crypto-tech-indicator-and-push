#!/usr/bin/env python3
"""Fetch 4-hour OHLCV data from CryptoCompare and compute RSI values.

The script queries CryptoCompare's ``histohour`` endpoint with ``aggregate=4``
to obtain 4-hour candles for several cryptocurrencies and calculates both
14-period and 6-period Relative Strength Indexes (RSI) from the closing prices.
Set the ``CC_API_KEY`` environment variable if you have an API key; the
endpoint can also work without a key but may be rate limited.
"""

from __future__ import annotations

import logging
import os
import time
import urllib.parse
from datetime import datetime
from typing import Any, Dict, Tuple

import pandas as pd
import requests

from config import shared
from rsi_utils import analyze_extreme_rsi, calculate_rsi

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Config:
    """Configuration for RSI-4h calculations.

    Global RSI thresholds and notification URLs are defined in
    :mod:`config.shared`; the values below are specific to the 4‑hour
    interval.
    """

    # Interval-specific API settings
    BASE_URL = "https://min-api.cryptocompare.com/data/v2/histohour"
    API_KEY = os.getenv("CC_API_KEY")
    API_CALL_DELAY = 5

    # Shared RSI thresholds
    RSI_OVERBOUGHT_14 = shared.RSI_OVERBOUGHT_14
    RSI_OVERSOLD_14 = shared.RSI_OVERSOLD_14
    RSI_OVERBOUGHT_6 = shared.RSI_OVERBOUGHT_6
    RSI_OVERSOLD_6 = shared.RSI_OVERSOLD_6

    # Shared notification endpoints
    NOTIFICATION_URLS = shared.NOTIFICATION_URLS


def fetch_ohlcv(symbol: str, limit: int = 100) -> pd.Series:
    """Fetch 4-hour OHLCV data for ``symbol`` and return close prices.

    Args:
        symbol: Cryptocurrency symbol (e.g., ``"BTC"``).
        limit: Number of 4-hour candles to retrieve.

    Returns:
        Series of closing prices indexed by candle open time.
    """
    params = {
        "fsym": symbol,
        "tsym": "USD",
        "limit": limit,
        "aggregate": 4,
    }
    headers = {"authorization": f"Apikey {Config.API_KEY}"} if Config.API_KEY else None

    logger.info("Requesting %s with params %s", Config.BASE_URL, params)
    response = requests.get(Config.BASE_URL, headers=headers, params=params, timeout=30)
    logger.info("Response status code: %s", response.status_code)
    response.raise_for_status()
    data = response.json()["Data"]["Data"]
    logger.info("Received %d data points", len(data))
    if data:
        logger.info("First record: %s", data[0])

    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df.set_index("time", inplace=True)
    return df["close"]


def format_rsi_message(extreme_rsi: Dict[str, str]) -> Tuple[str, str]:
    """Format extreme RSI readings into a Markdown message."""
    if not extreme_rsi:
        return "", ""

    overbought = {k: v for k, v in extreme_rsi.items() if "超买" in v}
    oversold = {k: v for k, v in extreme_rsi.items() if "超卖" in v}

    title = f"RSI-{len(overbought)}个超买,{len(oversold)}个超卖信号"
    lines = ["## RSI 4h 极值提醒", ""]

    if overbought:
        lines.append("### 🔴 超买 (卖出信号)")
        for k, v in overbought.items():
            lines.append(f"- {k}: {v}")
        lines.append("")

    if oversold:
        lines.append("### 🟢 超卖 (买入信号)")
        for k, v in oversold.items():
            lines.append(f"- {k}: {v}")
        lines.append("")

    lines.append(f"检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content = "\n".join(lines)
    return title, content


def send_notification(title: str, content: str) -> None:
    """Send the formatted message to all configured endpoints."""
    encoded_title = urllib.parse.quote_plus(title)
    encoded_content = urllib.parse.quote_plus(content)

    for name, url_tpl in Config.NOTIFICATION_URLS.items():
        url = url_tpl.format(encoded_title, encoded_content)
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                logger.info("%s 推送成功", name)
            else:
                logger.warning("%s 推送失败: %s", name, resp.status_code)
        except Exception as exc:
            logger.error("Notification error via %s: %s", name, exc)


SYMBOLS = ["BTC", "ETH", "BNB", "SOL"]


def main() -> None:
    results: Dict[str, Dict[str, Any]] = {}
    total = len(SYMBOLS)

    for idx, symbol in enumerate(SYMBOLS, 1):
        try:
            closes = fetch_ohlcv(symbol)
        except requests.RequestException as exc:
            logger.error("Failed to fetch %s data: %s", symbol, exc)
            results[symbol] = {"rsi_14": None, "rsi_6": None, "error": True}
        else:
            rsi14_series = calculate_rsi(closes, period=14)
            rsi6_series = calculate_rsi(closes, period=6)
            if rsi14_series is None or rsi6_series is None:
                results[symbol] = {"rsi_14": None, "rsi_6": None, "error": True}
            else:
                rsi14 = rsi14_series.iloc[-1]
                rsi6 = rsi6_series.iloc[-1]
                results[symbol] = {"rsi_14": rsi14, "rsi_6": rsi6, "error": False}
                print(f"{symbol}: RSI-14={rsi14:.2f}, RSI-6={rsi6:.2f}")

        if idx < total:
            time.sleep(Config.API_CALL_DELAY)

    extreme = analyze_extreme_rsi(results)
    if extreme:
        title, content = format_rsi_message(extreme)
        send_notification(title, content)


if __name__ == "__main__":
    main()

