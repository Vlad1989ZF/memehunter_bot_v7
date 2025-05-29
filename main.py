import time
import requests
from prettytable import PrettyTable

BOT_TOKEN = "7415348809:AAFsZdHeUffpdiEOfUuONEna72otR4m2G38"
CHAT_ID = "6945714975"
API_URL = "https://api-gateway-production-3b4d.up.railway.app/api/feeds"

pushed_symbols = set()

def fetch_tokens():
    try:
        res = requests.get(API_URL, timeout=10)
        res.raise_for_status()
        data = res.json()
        print(f"📌 接口返回 {len(data)} 条代币")
        return data
    except Exception as e:
        print(f"❌ 抓取失败: {e}")
        return []

def format_message(token):
    table = PrettyTable()
    table.field_names = ["项目", "信息"]
    table.align["项目"] = "l"
    table.align["信息"] = "l"

    table.add_row(["流动性", token.get("liquidity", "未知")])
    table.add_row(["市值", token.get("marketcap", "未知")])
    table.add_row(["Top10 持仓", token.get("top10_ratio", "未知")])
    table.add_row(["是否烧毁", "✅" if token.get("burned") else "❌"])
    table.add_row(["是否冻结", "✅" if token.get("frozen") else "❌"])
    table.add_row(["无Owner", "✅" if token.get("no_owner") else "❌"])

    msg = (
        f"🎖️ 综合评分: {token.get('score', '未知')}/100\n"
        f"📍代币: {token.get('name')} ({token.get('symbol')})\n\n"
        f"{table}\n\n"
        f"🔗 "
        f"{'[Twitter](' + token['socials'].get('twitter') + ')  ' if token.get('socials', {}).get('twitter') else ''}"
        f"{'[Telegram](' + token['socials'].get('telegram') + ')  ' if token.get('socials', {}).get('telegram') else ''}"
        f"{'[官网](' + token['socials'].get('website') + ')' if token.get('socials', {}).get('website') else ''}"
    )
    return msg

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(url, json=payload)
        print(f"✅ 推送状态: {res.status_code}")
    except Exception as e:
        print(f"❌ 推送失败: {e}")

if __name__ == "__main__":
    while True:
        tokens = fetch_tokens()
        for token in tokens:
            symbol = token.get("symbol")
            score = token.get("score", 0)
            if symbol in pushed_symbols:
                print(f"⏩ 跳过已推送代币: {symbol}")
                continue
            if score < 70:
                print(f"⚠️ 跳过低分代币: {symbol} (得分 {score})")
                continue
            msg = format_message(token)
            send_telegram(msg)
            pushed_symbols.add(symbol)
            print(f"🚀 推送完成: {symbol}")
        time.sleep(120)
