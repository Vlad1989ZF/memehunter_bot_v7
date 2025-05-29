import requests
import time
from prettytable import PrettyTable
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_URL = os.getenv("FEED_API", "https://api-gateway-production-3b4d.up.railway.app/api/feeds")

def fetch_data():
    try:
        res = requests.get(API_URL, timeout=10)
        if res.status_code == 200:
            return res.json()
        else:
            print("❌ 获取失败:", res.status_code)
    except Exception as e:
        print("❌ 异常:", e)
    return []

def format_message(token):
    table = PrettyTable()
    table.header = False
    table.border = False
    table.align = "l"

    table.add_row(["💧流动性:", token.get("liquidity", "未知")])
    table.add_row(["📈市值:", token.get("marketcap", "未知")])
    table.add_row(["👥Top10持仓:", token.get("top10_ratio", "未知")])
    table.add_row(["🔐丢权限:", "✅" if token.get("no_owner") else "❌"])
    table.add_row(["🔥烧池子:", "✅" if token.get("burned") else "❌"])
    table.add_row(["❄️无冻结:", "✅" if not token.get("frozen") else "❌"])

    socials = token.get("socials", {})
    links = []
    if socials.get("twitter"): links.append(f"[Twitter]({socials['twitter']})")
    if socials.get("telegram"): links.append(f"[Telegram]({socials['telegram']})")
    if socials.get("website"): links.append(f"[官网]({socials['website']})")
    link_line = " | ".join(links) if links else "暂无链接"

    msg = (
        f"🏅*综合评分:* {token.get('score', '?')}/100\n"
        f"💡*代币:* `{token.get('symbol', '?')}` | *{token.get('name', 'Unknown')}*\n"
        f"{table}\n\n"
        f"🔗 {link_line}"
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
        r = requests.post(url, json=payload)
        if r.status_code != 200:
            print("⚠️ 推送失败:", r.text)
        else:
            print("✅ 推送成功")
    except Exception as e:
        print("⚠️ 发送异常:", e)

def main():
    tokens = fetch_data()
    print(f"🎯 接口返回 {len(tokens)} 条代币")
    for token in tokens:
        score = token.get("score", 0)
        if score >= 70:
            msg = format_message(token)
            send_telegram(msg)
            time.sleep(1)

if __name__ == "__main__":
    main()
