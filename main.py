#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import requests
import logging

print("BOT_TOKEN:", repr(os.getenv("BOT_TOKEN")))
print("CHAT_ID:", repr(os.getenv("CHAT_ID")))
print("FEEDS_URL:", repr(os.getenv("FEEDS_URL")))


# ———— 配置 —————
BOT_TOKEN     = os.getenv("BOT_TOKEN")
CHAT_ID       = os.getenv("CHAT_ID")
FEEDS_URL     = os.getenv("FEEDS_URL")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 60))

if not all([BOT_TOKEN, CHAT_ID, FEEDS_URL]):
    raise RuntimeError("需要设置 BOT_TOKEN、CHAT_ID、FEEDS_URL 三个环境变量")
    
BASE_TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
SEND_API = BASE_TELEGRAM_URL + "/sendMessage"

# 日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("memehunter_bot_v7")

# 用于去重
sent_set = set()

def fetch_feeds():
    """从聚合接口拿数据"""
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
    """根据单个 token 生成要推送的文本"""
    # 评分
    score = item.get("score", 0)
    # 基本信息
    name = item.get("name", "Unknown")
    symbol = item.get("symbol", "")
    marketcap = item.get("marketcap", "未知")
    liquidity = item.get("liquidity", "未知")
    top10 = item.get("top10_ratio", "未知")
    burned = "✅" if item.get("burned") else "❌"
    frozen = "✅" if item.get("frozen") else "❌"
    no_owner = "✅" if item.get("no_owner") else "❌"
    # 社交
    socials = item.get("socials", {})
    twitter = socials.get("twitter", "")
    telegram = socials.get("telegram", "")
    website = socials.get("website", "")
    # 构建评分明细表格
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
    """调用 Telegram Bot API 发送消息"""
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
            # 唯一标识：symbol+timestamp
            key = f"{item.get('symbol')}_{item.get('timestamp')}"
            if key in sent_set:
                continue
            # 只推送新的
            sent_set.add(key)
            msg = build_message(item)
            send_telegram(msg)
            time.sleep(1)  # 避免瞬间多条被 Telegram 拒
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        logger.info("程序手动退出")
    except Exception:
        logger.exception("未捕获异常，程序退出")

