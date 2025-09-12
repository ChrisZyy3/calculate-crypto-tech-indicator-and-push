# 加密货币RSI技术指标计算与推送工具

这是一个用于计算加密货币RSI（相对强弱指数）技术指标并发送通知的Python工具。

## 功能特性

- 🔢 计算RSI-14和RSI-6指标
- 📊 支持多种主流加密货币
- 🚨 自动检测超买/超卖信号
- 📱 支持多个推送接口（Server酱 + push.ft07.com）
- 🛠️ 模块化代码设计
- 📝 完整的日志记录
- 🔄 自动重试机制
- 🔒 完善的URL编码处理

## 支持的加密货币
### 参考https://docs.google.com/spreadsheets/d/1wTTuxXt8n9q7C4NDXqQpI3wpKu1_5bGVmP9Xz0XGSyU/edit?pli=1&gid=0#gid=0
- BTC (Bitcoin)
- ETH (Ethereum) 
- BNB (Binance Coin)
- SOL (Solana)
- JLP (Jupiter Perpetuals LP Token)
- PENDLE (Pendle)
- SUI (Sui)
- APT (Aptos)
- PENPIE (Penpie)
- EQB (Equilibria Finance)
- DEEP (Deep)
- WAL (Walrus)
- BGB (Bitget Token)
- MNT (Mantle)
- SPK (Spark)

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python rsi1d.py
```

## 配置说明

代码中的`Config`类包含了所有可配置参数：

- **RSI阈值**：
  - RSI-14 超买阈值：65
  - RSI-14 超卖阈值：35
  - RSI-6 超买阈值：70
  - RSI-6 超卖阈值：30

- **API配置**：
  - 请求超时：30秒
  - 重试次数：3次
  - API调用间隔：20秒

- **推送配置**：
  - Server酱接口：默认启用
  - push.ft07.com接口：默认启用
  - 同时支持多个接口推送，提高可靠性

## 代码优化

优化后的代码具有以下改进：

1. **模块化设计**：将功能拆分为独立的函数
2. **错误处理**：添加了完整的异常处理和重试机制
3. **类型注解**：增加了类型提示提高代码可读性
4. **日志记录**：使用logging模块记录运行状态
5. **配置管理**：统一的配置类管理所有参数
6. **代码重构**：消除了重复代码，提高了可维护性

## 输出示例

```
2025-09-12 10:30:00 - INFO - Starting RSI calculation and notification service...
2025-09-12 10:30:01 - INFO - Processing BTC (1/15)...
2025-09-12 10:30:02 - INFO - RSI-14 for BTC: 45.23
2025-09-12 10:30:02 - INFO - RSI-6 for BTC: 52.11
...
==================================================
RSI 结果摘要
==================================================

RSI-14 Results:
------------------------------
     BTC:  45.23
     ETH:  38.45
...
```

## 推送标题与内容

- 标题: 使用动态计数格式 `RSI-x个超买,y个超卖信号`（例如：`RSI-2个超买,1个超卖信号`）。
- 内容: Markdown 格式，包含检测时间、超买/超卖表格、建议与指标说明。
- 示例: 参见 `markdown_demo.md` 查看完整渲染示例。
- 兼容性: 发送前对 `title` 与 `content` 做 URL 编码，适配 Server酱 和 push.ft07 平台。

## 注意事项

1. 请确保网络连接正常，API调用需要访问CoinGecko
2. 推送功能支持多个接口：
   - Server酱：默认启用
   - push.ft07.com：默认启用
   - 只要有一个接口成功即认为推送成功
3. 如需修改推送配置，请更新`Config.NOTIFICATION_URLS`字典
4. 建议在服务器上定期运行以获得及时的RSI提醒

## 推送接口配置

当前支持的推送接口：

| 接口名称 | 描述 | URL格式 |
|----------|------|----------|
| server_chan | Server酱官方接口 | `https://sctapi.ftqq.com/{key}.send` |
| push_ft07 | push.ft07.com接口 | `https://{uid}.push.ft07.com/send/{sendkey}.send` |

程序会同时向所有配置的接口发送通知，提高消息到达率。
