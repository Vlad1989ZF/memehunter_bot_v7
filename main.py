import os
import time
import requests
import telegram
from tabulate import tabulate

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_URL = os.getenv("API_URL", "https://api-gateway-production-3b4d.up.railway.app/api/feeds")
SCORE_THRESHOLD = 70

bot = telegram.Bot(token=BOT_TOKEN)

def fetch_data():
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[错误] 获取数据失败: {e}")
        return []

def build_message(token):
    socials = token.get("socials", {})
    score = max(0, min(100, token.get("score", 0)))
    table = tabulate([
        ["评分", f"{score}"],
        ["市值", token.get("marketcap", "未知")],
        ["流动性", token.get("liquidity", "未知")],
        ["Top10占比", token.get("top10_ratio", "未知")],
        ["是否销毁", "✅" if token.get("burned") else "❌"],
        ["是否冻结", "✅" if token.get("frozen") else "❌"],
        ["无Owner", "✅" if token.get("no_owner") else "❌"]
    ], headers=["项目", "信息"], tablefmt="github")

    msg = (
print(f"💥发现潜力代币！")

        f"名称: {token.get('name')} (`{token.get('symbol')}`)

"
        f"{table}

"
        f"🔗 社交媒体:
"
        f"{'🌐 官网: ' + socials.get('website') if socials.get('website') else ''}
"
        f"{'🐦 推特: ' + socials.get('twitter') if socials.get('twitter') else ''}
"
        f"{'💬 电报: ' + socials.get('telegram') if socials.get('telegram') else ''}
"
    )
    return msg

def main_loop():
    sent_tokens = set()
    while True:
        tokens = fetch_data()
        for token in tokens:
            symbol = token.get("symbol")
            score = token.get("score", 0)
            if symbol and score >= SCORE_THRESHOLD and symbol not in sent_tokens:
                msg = build_message(token)
                try:
                    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode=telegram.constants.ParseMode.MARKDOWN)
                    sent_tokens.add(symbol)
                    print(f"[推送成功] {symbol}")
                except Exception as e:
                    print(f"[推送失败] {symbol}: {e}")
        time.sleep(60)

if __name__ == "__main__":
    main_loop()
