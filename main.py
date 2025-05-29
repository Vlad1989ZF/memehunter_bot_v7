#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import requests
import logging

BOT_TOKEN     = os.getenv("BOT_TOKEN")
CHAT_ID       = os.getenv("CHAT_ID")
FEEDS_URL     = os.getenv("FEEDS_URL")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 60))

if not all([BOT_TOKEN, CHAT_ID, FEEDS_URL]):
    raise RuntimeError("需要设置 BOT_TOKEN、CHAT_ID、FEEDS_URL 三个环境变量")

BASE_TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
SEND_API = BASE_TELEGRAM_URL + "/sendMessage"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("memehunter_bot_v7")

sent_set = set()

def fetch_feeds():
    try:
        r = requests.get(FEEDS_URL, timeout=10)
        r.raise_for_status()
        data = r.json()
        logger.info(f"接口返回 {len(data)} 条代币")
        return data
    except Exception as e:
        logger.warning(f"⚠️ 取接口失败: {e}")
        return []

def build_message(item):
    symbol = item.get("symbol", "")
    name = item.get("name", "Unknown")
    marketcap = item.get("dex_marketcap", item.get("marketcap", "未知"))
    liquidity = item.get("dex_liquidity", item.get("liquidity", "未知"))
    top10 = item.get("top10_ratio", "未知")
    burned = "✅" if item.get("burned") else "❌"
    frozen = "✅" if item.get("frozen") else "❌"
    no_owner = "✅" if item.get("no_owner") else "❌"

    try:
        mc = float(str(marketcap).replace("$", "").replace("K", "e3").replace("M", "e6"))
        liq = float(str(liquidity).replace("$", "").replace("K", "e3").replace("M", "e6"))
        score = int(min(100, (mc + liq) / 1e6))
    except:
        score = 0

    socials = item.get("socials", {})
    twitter = socials.get("twitter", "")
    telegram = socials.get("telegram", "")
    website = socials.get("website", "")

    table = (
        f"🏆 综合评分: *{score}/100*\n"
    f"🔖 名称: [{name}](https://www.google.com/search?q={symbol}) `{symbol}`\n"
    f"💧 市值: {marketcap}    💰 流动性: {liquidity}\n"
    f"👑 Top10 持有: {top10}\n"
    f"🚫 销毁: {burned}    ❄️ 冻结: {frozen}\n"
    f"🔑 无owner: {no_owner}\n\n"
    f"🔗 社交 | [Twitter]({twitter}) | [Telegram]({telegram}) | [官网]({website})"
    )
    return table

def send_telegram(msg: str):
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        r = requests.post(SEND_API, json=payload, timeout=10)
        r.raise_for_status()
        logger.info("✅ 推送成功")
    except Exception as e:
        logger.error(f"❌ 推送失败: {e} -- 数据: {msg[:50]}")

def main_loop():
    logger.info("🚀 MemeHunter Bot v7 启动")
    while True:
        feeds = fetch_feeds()
        for item in feeds:
            key = item.get('symbol')
            if key in sent_set:
                continue
            sent_set.add(key)
            msg = build_message(item)
            send_telegram(msg)
            time.sleep(1)
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        logger.info("程序手动退出")
    except Exception:
        logger.exception("未捕获异常，程序退出")

