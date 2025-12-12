import os
import re
import requests
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import TELEGRAM_TOKEN, TARGET_CHAT_ID

# 初始化bot
bot = Bot(token=TELEGRAM_TOKEN)

def extract_app_id(url):
    """从App Store链接中提取ID"""
    match = re.search(r'id(\d+)', url)
    return match.group(1) if match else None

def get_app_price(app_id):
    """获取App价格信息"""
    url = f"https://itunes.apple.com/lookup?id={app_id}&country=cn"
    response = requests.get(url)
    data = response.json()
    if data['resultCount'] > 0:
        app = data['results'][0]
        return {
            'name': app.get('trackName'),
            'price': app.get('price', 0),
            'currency': app.get('currency'),
            'url': app.get('trackViewUrl')
        }
    return None

def handle_message(update: Update, context: CallbackContext):
    """处理用户消息"""
    if update.message.text.startswith('/p'):
        url = update.message.text[3:].strip()
        app_id = extract_app_id(url)
        
        if app_id:
            price_info = get_app_price(app_id)
            if price_info:
                response = (
                    f"📱 App名称: {price_info['name']}\n"
                    f"💰 价格: {price_info['price']} {price_info['currency']}\n"
                    f"🔗 链接: {price_info['url']}"
                )
                # 回复用户
                update.message.reply_text(response)
                # 转发到目标群组
                bot.send_message(
                    chat_id=TARGET_CHAT_ID,
                    text=f"新价格查询:\n{response}\n\n来自用户: @{update.message.from_user.username}"
                )
            else:
                update.message.reply_text("⚠️ 无法获取应用价格信息")
        else:
            update.message.reply_text("❌ 无效的App Store链接")

def main():
    """启动机器人"""
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()