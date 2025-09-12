#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多接口推送功能
"""

from rsi1d import send_notification, Config
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_multi_push():
    """测试多接口推送"""
    print("=" * 60)
    print("测试多接口推送功能")
    print("=" * 60)
    
    print(f"配置的推送接口数量: {len(Config.NOTIFICATION_URLS)}")
    for name in Config.NOTIFICATION_URLS.keys():
        print(f"- {name}")
    print()
    
    # 测试内容
    title = "测试双接口推送"
    content = """BTC (RSI-14): 超买: 75.50
ETH (RSI-6): 超卖: 25.30

检测时间: 2025-09-12 14:30:00"""
    
    print("开始发送测试消息...")
    result = send_notification(title, content)
    
    print(f"推送结果: {'成功' if result else '失败'}")
    print("=" * 60)

if __name__ == "__main__":
    test_multi_push()