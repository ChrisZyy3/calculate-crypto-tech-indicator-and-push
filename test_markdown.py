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
    test_extreme_rsi = {
        "BTC (RSI-14)": "超买: 72.50",
        "ETH (RSI-6)": "超卖: 28.30",
        "SOL (RSI-14)": "超买: 68.20",
        "APT (RSI-6)": "超卖: 25.80"
    }
    
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