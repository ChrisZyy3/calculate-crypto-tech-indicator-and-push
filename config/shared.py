"""Global configuration shared by RSI scripts.

This module holds constants that are reused across different
interval scripts, such as RSI thresholds and notification endpoints.
"""

# RSI threshold settings used by both 1d and 4h scripts
RSI_OVERBOUGHT_14 = 65
RSI_OVERSOLD_14 = 35
RSI_OVERBOUGHT_6 = 70
RSI_OVERSOLD_6 = 30

# Notification endpoints (e.g., Server酱 / PushDeer)
NOTIFICATION_URLS = {
    # 'server_chan': "https://sctapi.ftqq.com/XXX.send?title={}&desp={}",
    'push_ft07': (
        "https://sctp11310thhgz5tizmjdsetszjitcko.push.ft07.com/send/"
        "sctp11310thhgz5tizmjdsetszjitcko.send?title={}&desp={}"
    ),
}
