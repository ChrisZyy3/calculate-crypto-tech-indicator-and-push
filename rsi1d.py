"""RSI 日线脚本

Global thresholds and notification URLs are defined in
``config.shared``. The settings below are specific to the daily
interval such as API endpoints, delays and crypto mappings.
"""

import requests
import pandas as pd
import time
import urllib.parse
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime

from config import shared

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Config:
    # API配置（日线特有）
    COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
    REQUEST_TIMEOUT = 30
    RETRY_ATTEMPTS = 3

    # RSI配置
    DEFAULT_RSI_PERIODS = [14, 6]
    DEFAULT_DAYS = 30

    # 阈值配置（全局）
    RSI_OVERBOUGHT_14 = shared.RSI_OVERBOUGHT_14
    RSI_OVERSOLD_14 = shared.RSI_OVERSOLD_14
    RSI_OVERBOUGHT_6 = shared.RSI_OVERBOUGHT_6
    RSI_OVERSOLD_6 = shared.RSI_OVERSOLD_6

    # 通知配置（全局）
    NOTIFICATION_URLS = shared.NOTIFICATION_URLS

    # 延迟配置（日线特有）
    API_CALL_DELAY = 20  # 秒

    # 加密货币配置（日线特有）
    CRYPTO_IDS = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "BNB": "binancecoin",
        "SOL": "solana",
        "JLP": "jupiter-perpetuals-liquidity-provider-token",
        "PENDLE": "pendle",
        "PENPIE": "penpie",
        "EQB": "equilibria-finance",
        "SUI": "sui",
        "APT": "aptos",
        "DEEP": "deep",
        "WAL": "walrus-2",
        "BGB": "bitget-token",
        "MNT": "mantle",
        "SPK": "spark-2",
        "WLD": 'worldcoin-wld',
        "ENA": 'ethena',
    }

def get_historical_prices(coin_id: str, days: int = Config.DEFAULT_DAYS) -> Optional[pd.Series]:
    """
    获取历史价格数据
    
    Args:
        coin_id: CoinGecko的币种ID
        days: 获取天数
    
    Returns:
        价格数据Series，如果失败返回None
    """
    url = f"{Config.COINGECKO_BASE_URL}/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': days,
        'interval': 'daily'
    }
    
    for attempt in range(Config.RETRY_ATTEMPTS):
        try:
            response = requests.get(url, params=params, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            if 'prices' not in data or not data['prices']:
                logger.warning(f"No price data found for {coin_id}")
                return None
                
            prices = data['prices']
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])  # type: ignore
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('date', inplace=True)
            
            price_series = df['price']  # type: ignore
            return price_series  # type: ignore
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed for {coin_id}: {e}")
            if attempt < Config.RETRY_ATTEMPTS - 1:
                time.sleep(2 ** attempt)  # 指数退避
            else:
                logger.error(f"Failed to fetch data for {coin_id} after {Config.RETRY_ATTEMPTS} attempts")
                return None
        except Exception as e:
            logger.error(f"Unexpected error fetching data for {coin_id}: {e}")
            return None
    
    return None

def calculate_rsi(prices: pd.Series, length: int = 14) -> Optional[float]:
    """
    Calculate RSI using TradingView's algorithm (ta.rsi equivalent)
    This uses RMA (Running Moving Average) which is equivalent to EMA with alpha = 1/length
    
    Args:
        prices: 价格数据Series
        length: RSI计算周期
    
    Returns:
        最新的RSI值，如果计算失败返回None
    """
    if prices is None or len(prices) < length + 1:
        logger.warning(f"Insufficient data for RSI calculation. Need at least {length + 1} data points, got {len(prices) if prices is not None else 0}")
        return None
    
    try:
        # Calculate price changes
        delta = prices.diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate RMA (Running Moving Average) - TradingView's method
        # RMA is equivalent to EMA with alpha = 1/length
        alpha = 1.0 / length
        
        # Initialize the first values
        avg_gain = gain.ewm(alpha=alpha, adjust=False).mean()
        avg_loss = loss.ewm(alpha=alpha, adjust=False).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi_series = 100 - (100 / (1 + rs))
        
        # 返回最新的RSI值
        if hasattr(rsi_series, 'iloc') and len(rsi_series) > 0:  # type: ignore
            latest_rsi = rsi_series.iloc[-1]  # type: ignore
            return latest_rsi if pd.notna(latest_rsi) else None
        else:
            return None
        
    except Exception as e:
        logger.error(f"Error calculating RSI: {e}")
        return None

def calculate_crypto_rsi(crypto_ids: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
    """
    计算多个加密货币的RSI值
    
    Args:
        crypto_ids: 币种符号到CoinGecko ID的映射
    
    Returns:
        包含RSI结果的字典
    """
    results = {}
    total_cryptos = len(crypto_ids)
    
    for idx, (symbol, coin_id) in enumerate(crypto_ids.items(), 1):
        logger.info(f"Processing {symbol} ({idx}/{total_cryptos})...")
        
        try:
            # 获取历史价格
            prices = get_historical_prices(coin_id, days=Config.DEFAULT_DAYS)
            
            if prices is None:
                results[symbol] = {
                    'rsi_14': "Failed to fetch data",
                    'rsi_6': "Failed to fetch data",
                    'error': True
                }
                continue
            
            # 计算RSI-14和RSI-6
            rsi_14 = calculate_rsi(prices, length=14)
            rsi_6 = calculate_rsi(prices, length=6)
            
            results[symbol] = {
                'rsi_14': rsi_14,
                'rsi_6': rsi_6,
                'error': False
            }
            
            # 输出结果
            if rsi_14 is not None:
                logger.info(f"RSI-14 for {symbol}: {rsi_14:.2f}")
            else:
                logger.warning(f"Failed to calculate RSI-14 for {symbol}")
                
            if rsi_6 is not None:
                logger.info(f"RSI-6 for {symbol}: {rsi_6:.2f}")
            else:
                logger.warning(f"Failed to calculate RSI-6 for {symbol}")
                
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
            results[symbol] = {
                'rsi_14': f"Error: {e}",
                'rsi_6': f"Error: {e}",
                'error': True
            }
        
        # 添加延迟（除了最后一个）
        if idx < total_cryptos:
            logger.info(f"Waiting {Config.API_CALL_DELAY} seconds before next request...")
            time.sleep(Config.API_CALL_DELAY)
    
    return results

def analyze_extreme_rsi(results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    """
    分析极端RSI值
    
    Args:
        results: RSI计算结果
    
    Returns:
        极端RSI值的字典
    """
    extreme_rsi = {}
    
    for symbol, data in results.items():
        if data['error']:
            continue
            
        # 检查RSI-14
        rsi_14 = data['rsi_14']
        if isinstance(rsi_14, float):
            if rsi_14 >= Config.RSI_OVERBOUGHT_14:
                extreme_rsi[f"{symbol} (RSI-14)"] = f"超买: {rsi_14:.2f}"
            elif rsi_14 <= Config.RSI_OVERSOLD_14:
                extreme_rsi[f"{symbol} (RSI-14)"] = f"超卖: {rsi_14:.2f}"
        
        # 检查RSI-6
        rsi_6 = data['rsi_6']
        if isinstance(rsi_6, float):
            if rsi_6 >= Config.RSI_OVERBOUGHT_6:
                extreme_rsi[f"{symbol} (RSI-6)"] = f"超买: {rsi_6:.2f}"
            elif rsi_6 <= Config.RSI_OVERSOLD_6:
                extreme_rsi[f"{symbol} (RSI-6)"] = f"超卖: {rsi_6:.2f}"
    
    return extreme_rsi

def format_rsi_message(extreme_rsi: Dict[str, str]) -> Tuple[str, str]:
    """
    格式化RSI消息为Markdown格式
    
    Args:
        extreme_rsi: 极端RSI值字典
    
    Returns:
        元组(title, content)
    """
    if not extreme_rsi:
        return "", ""
    
    # 分类统计
    overbought_items = []
    oversold_items = []
    
    for indicator, status in extreme_rsi.items():
        if "超买" in status:
            # 提取RSI值
            rsi_value = status.split(': ')[1]
            overbought_items.append((indicator, rsi_value))
        elif "超卖" in status:
            # 提取RSI值
            rsi_value = status.split(': ')[1]
            oversold_items.append((indicator, rsi_value))
    
    # 计算并设置标题：RSI-x个超买,y个超卖信号
    title = f"RSI-{len(overbought_items)}个超买,{len(oversold_items)}个超卖信号"

    # 构建 Markdown 内容
    content_lines = [
        "## 📈 RSI技术指标分析",
        "",
        f"🕰️ **检测时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        ""
    ]
    
    # 超买区域 (红色)
    if overbought_items:
        content_lines.extend([
            "### 🔴 **超买区域** `卖出信号`",
            "",
            "| 加密货币 | RSI指标 | RSI值 |",
            "|---------|--------|-------|"
        ])
        
        for indicator, rsi_value in overbought_items:
            # 解析指标名称
            parts = indicator.split(' (')
            crypto_name = parts[0]
            rsi_type = parts[1].rstrip(')')
            
            content_lines.append(
                f"| **{crypto_name}** | `{rsi_type}` | **{rsi_value}** |"
            )
        
        content_lines.extend(["", "> 📉 **建议**: 考虑卖出，获利了结", ""])
    
    # 超卖区域 (绿色)
    if oversold_items:
        content_lines.extend([
            "### 🟢 **超卖区域** `买入信号`",
            "",
            "| 加密货币 | RSI指标 | RSI值 |",
            "|---------|--------|-------|"
        ])
        
        for indicator, rsi_value in oversold_items:
            # 解析指标名称
            parts = indicator.split(' (')
            crypto_name = parts[0]
            rsi_type = parts[1].rstrip(')')
            
            content_lines.append(
                f"| **{crypto_name}** | `{rsi_type}` | **{rsi_value}** |"
            )
        
        content_lines.extend(["", "> 📈 **建议**: 考虑买入，可能将反弹", ""])
    
    # 添加脚注
    content_lines.extend([
        "---",
        "",
        "### 📊 RSI指标说明",
        "",
        "- **RSI-14**: 14日相对强弱指数 (超买: ≥ 65, 超卖: ≤ 35)",
        "- **RSI-6**: 6日相对强弱指数 (超买: ≥ 70, 超卖: ≤ 30)",
        "",
        "> ⚠️ **免责声明**: 仅供参考，不构成投资建议，请理性投资。"
    ])
    
    content = "\n".join(content_lines)
    return title, content

def send_notification(title: str, content: str) -> bool:
    """
    发送通知到多个接口
    
    Args:
        title: 通知标题
        content: 通知内容
    
    Returns:
        是否至少有一个接口发送成功
    """
    # 记录原始内容信息
    logger.info(f"Preparing to send notification with title: {title}")
    newline_count = content.count('\n')
    logger.info(f"Content has {len(content)} characters and {newline_count} line breaks")
    
    # URL编码 - 使用quote_plus确保所有特殊字符(包括换行符、空格等)都被正确编码
    encoded_title = urllib.parse.quote_plus(title)
    encoded_content = urllib.parse.quote_plus(content)
    
    logger.info(f"Encoded title: {encoded_title[:100]}...")  # 只显示前100个字符
    logger.info(f"Encoded content length: {len(encoded_content)} characters")
    
    success_count = 0
    total_apis = len(Config.NOTIFICATION_URLS)
    
    # 尝试所有推送接口
    for api_name, url_template in Config.NOTIFICATION_URLS.items():
        try:
            # 发送通知
            notification_url = url_template.format(encoded_title, encoded_content)
            logger.info(f"Sending to {api_name}: {notification_url[:100]}...")
            
            response = requests.get(notification_url, timeout=Config.REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                logger.info(f"{api_name} 推送成功!")
                
                # 记录响应内容以便调试
                try:
                    response_data = response.json()
                    if response_data.get('code') == 0 or response_data.get('errno') == 0:
                        logger.info(f"{api_name} 服务器确认成功")
                    else:
                        logger.warning(f"{api_name} 返回非成功状态: {response_data}")
                except:
                    logger.info(f"{api_name} 响应解析完成，推送应该已发送")
                
                success_count += 1
            else:
                logger.error(f"{api_name} 推送失败: HTTP {response.status_code}")
                logger.error(f"{api_name} 响应内容: {response.text[:200]}...")  # 只显示前200个字符
                
        except Exception as e:
            logger.error(f"{api_name} 推送时出错: {e}")
    
    # 返回结果
    if success_count > 0:
        logger.info(f"推送完成: {success_count}/{total_apis} 个接口成功")
        return True
    else:
        logger.error("所有推送接口都失败")
        return False

def print_results_summary(results: Dict[str, Dict[str, Any]]):
    """
    打印结果摘要
    
    Args:
        results: RSI计算结果
    """
    print("\n" + "=" * 50)
    print("RSI 结果摘要")
    print("=" * 50)
    
    # RSI-14结果
    print("\nRSI-14 Results:")
    print("-" * 30)
    for symbol, data in results.items():
        rsi_14 = data['rsi_14']
        if isinstance(rsi_14, float):
            print(f"{symbol:>8}: {rsi_14:>6.2f}")
        else:
            print(f"{symbol:>8}: {str(rsi_14)}")
    
    # RSI-6结果
    print("\nRSI-6 Results:")
    print("-" * 30)
    for symbol, data in results.items():
        rsi_6 = data['rsi_6']
        if isinstance(rsi_6, float):
            print(f"{symbol:>8}: {rsi_6:>6.2f}")
        else:
            print(f"{symbol:>8}: {str(rsi_6)}")

def main():
    """
    主函数
    """
    logger.info("Starting RSI calculation and notification service...")
    
    # 加密货币配置
    crypto_ids = Config.CRYPTO_IDS
    
    try:
        # 计算RSI
        results = calculate_crypto_rsi(crypto_ids)
        
        # 打印结果摘要
        print_results_summary(results)
        
        # 分析极端RSI值
        extreme_rsi = analyze_extreme_rsi(results)
        
        # 处理通知
        if extreme_rsi:
            # 使用新的Markdown格式化函数
            title, content = format_rsi_message(extreme_rsi)
            
            # 打印最终需要发送的消息
            print("\n" + "=" * 50)
            print("最终发送的通知消息")
            print("=" * 50)
            print(f"标题: {title}")
            print(f"内容:\n{content}")
            print("=" * 50)
            
            # 发送提醒
            send_notification(title, content)
            
        else:
            print("\n" + "=" * 50)
            print("最终发送的通知消息")
            print("=" * 50)
            print("没有发现极端RSI值，无需发送提醒。")
            print("=" * 50)
            
    except Exception as e:
        logger.error(f"Main execution error: {e}")
        raise

if __name__ == "__main__":
    main()
