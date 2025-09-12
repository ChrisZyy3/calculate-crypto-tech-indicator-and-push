#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URL编码测试脚本
演示如何正确编码包含换行符、特殊字符和中文的内容
"""

import urllib.parse

def test_encoding():
    """测试不同编码方法的效果"""
    
    # 测试内容 - 包含中文、英文、特殊字符、换行符
    title = "加密货币RSI提醒 - 测试标题 & 符号!"
    content = """以下加密货币的RSI值处于极端区域:

BTC (RSI-14): 超买: 75.50
ETH (RSI-6): 超卖: 25.30
SOL (RSI-14): 超买: 68.20

检测时间: 2025-09-12 10:30:00
"""

    print("=" * 80)
    print("URL编码测试对比")
    print("=" * 80)
    
    print(f"原始标题: {title}")
    print(f"原始内容长度: {len(content)} 字符")
    print(f"换行符数量: {content.count(chr(10))} 个")
    print()
    
    # 使用不同的编码方法
    methods = [
        ("quote", urllib.parse.quote),
        ("quote_plus", urllib.parse.quote_plus),
    ]
    
    for method_name, method_func in methods:
        print(f"--- 使用 {method_name} 编码 ---")
        encoded_title = method_func(title)
        encoded_content = method_func(content)
        
        print(f"编码后标题: {encoded_title}")
        print(f"编码后内容长度: {len(encoded_content)} 字符")
        print(f"编码后内容前100字符: {encoded_content[:100]}...")
        print()
    
    # 验证解码
    print("--- 解码验证 ---")
    encoded = urllib.parse.quote_plus(content)
    decoded = urllib.parse.unquote_plus(encoded)
    print(f"编码->解码是否一致: {content == decoded}")
    print()
    
    # 显示URL构建示例
    print("--- 完整URL示例 ---")
    base_url = "https://sctapi.ftqq.com/SCT241317TwvSKJKGGttpZcEe2j9CQgjDo.send"
    encoded_title = urllib.parse.quote_plus(title)
    encoded_content = urllib.parse.quote_plus(content)
    
    full_url = f"{base_url}?title={encoded_title}&desp={encoded_content}"
    print(f"完整URL长度: {len(full_url)} 字符")
    print(f"URL前150字符: {full_url[:150]}...")
    print()

if __name__ == "__main__":
    test_encoding()