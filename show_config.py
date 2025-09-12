#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看推送接口配置
"""

from rsi1d import Config

def show_config():
    print("=" * 60)
    print("当前推送接口配置")
    print("=" * 60)
    
    for name, url in Config.NOTIFICATION_URLS.items():
        print(f"{name}:")
        print(f"  URL: {url}")
        print()
    
    print(f"总计配置了 {len(Config.NOTIFICATION_URLS)} 个推送接口")

if __name__ == "__main__":
    show_config()