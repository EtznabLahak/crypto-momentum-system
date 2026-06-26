import aiohttp

TELEGRAM_BOT_TOKEN = "8926781608:AAG6wqCTjQ4FYWWq60hsIpytlsCSaibLCco"

TELEGRAM_CHAT_IDS = [
    "365661286",
    "8697841471"
]


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