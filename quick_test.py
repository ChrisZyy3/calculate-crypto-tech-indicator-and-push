#!/usr/bin/env python3
import sys
if 'rsi1d' in sys.modules:
    del sys.modules['rsi1d']

from rsi1d import format_rsi_message

test_data = [
    {
        'symbol': 'BTC',
        'indicator': 'RSI-14',
        'signal': '超买',
        'rsi_value': 72.50,
        'price': 63123.45,
    }
]
title, content = format_rsi_message(test_data)

if '<font color=' in content:
    print("❌ 仍包含颜色标签")
else:
    print("✅ 已移除颜色标签")

print(
    "RSI值部分:",
    [line for line in content.split('\n') if 'BTC' in line][0]
    if any('BTC' in line for line in content.split('\n'))
    else "未找到",
)

if '最新价格' in content and '$63,123.45' in content:
    print("✅ 包含最新价格列")
else:
    print("❌ 未包含最新价格列")
