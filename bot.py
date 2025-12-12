import os
import re
import requests
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 从环境变量获取配置
BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")

async def extract_and_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.replace("/p", "").strip()
    
    # 提取Apple Store ID
    app_id = re.search(r'/id(\d+)', url)
    if not app_id:
        await update.message.reply_text("⚠️ 无效的App Store链接")
        return
    
    app_id = app_id.group(1)
    
    # 获取价格信息
    try:
        price = get_app_price(app_id)
        message = f"🛒 App ID: {app_id}\n💰 价格: {price}\n🔗 链接: {url}"
        
        # 转发到目标群组
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(chat_id=TARGET_CHAT_ID, text=message)
        await update.message.reply_text("✅ 已获取并转发价格信息")
    except Exception as e:
        await update.message.reply_text(f"❌ 获取价格失败: {str(e)}")

def get_app_price(app_id: str) -> str:
    """通过Apple Store API获取价格"""
    api_url = f"https://itunes.apple.com/lookup?id={app_id}"
    response = requests.get(api_url).json()
    
    if not response.get("results"):
        raise ValueError("未找到应用信息")
    
    return response["results"][0].get("formattedPrice", "免费")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("p", extract_and_forward))
    app.run_polling()

if __name__ == "__main__":
    main()