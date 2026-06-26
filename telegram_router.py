from dotenv import load_dotenv
import os
import aiohttp

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_IDS = os.getenv("TELEGRAM_CHAT_IDS").split(",")


async def send_telegram(message):

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    async with aiohttp.ClientSession() as session:

        for chat_id in TELEGRAM_CHAT_IDS:

            payload = {
                "chat_id": chat_id,
                "text": message,
                "disable_web_page_preview": True
            }

            try:

                async with session.post(url, data=payload):
                    pass

            except Exception as e:
                print(f"Telegram Error: {e}")