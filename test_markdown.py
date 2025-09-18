#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Markdown格式的RSI推送消息
"""

from rsi1d import format_rsi_message, send_notification
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_markdown_formatting():
    """测试Markdown格式化"""
    print("=" * 60)
    print("测试Markdown格式的RSI消息")
    print("=" * 60)
    
    # 模拟极端RSI数据
    test_extreme_rsi = [
        {"symbol": "BTC", "indicator": "RSI-14", "signal": "超买", "rsi_value": 72.50, "price": 63123.45},
        {"symbol": "ETH", "indicator": "RSI-6", "signal": "超卖", "rsi_value": 28.30, "price": 3123.11},
        {"symbol": "SOL", "indicator": "RSI-14", "signal": "超买", "rsi_value": 68.20, "price": 154.92},
        {"symbol": "APT", "indicator": "RSI-6", "signal": "超卖", "rsi_value": 25.80, "price": 9.82},
    ]
    
    # 格式化消息
    title, content = format_rsi_message(test_extreme_rsi)
    
    print(f"标题: {title}")
    print()
    print("Markdown内容:")
    print("-" * 40)
    print(content)
    print("-" * 40)
    print()
    
    # 测试发送
    print("正在发送测试消息...")
    result = send_notification(title, content)
    
    print(f"发送结果: {'成功' if result else '失败'}")
    print("=" * 60)

if __name__ == "__main__":
    test_markdown_formatting()
