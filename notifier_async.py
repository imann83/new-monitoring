
import aiohttp
import logging
import asyncio

class AsyncNotifier:
    def __init__(self):
        self.telegram_token = "7794367450:AAG4-FJbNRGja9xbglkgFtE_hyB1Tohb7C8"
        self.chat_id = "887116840"
        self.pushover_user = "uuhb4p38no4o13os33uakfe5su3ed4"
        self.pushover_token = "a5u6n3uhp19izybbhkojqkbfh25ff5"

    async def send(self, message: str):
        await asyncio.gather(
            self.send_telegram(message),
            self.send_pushover(message)
        )

    async def send_telegram(self, message):
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(f"https://api.telegram.org/bot{self.telegram_token}/sendMessage", data={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True
                }, timeout=5)
        except Exception as e:
            logging.error(f"Telegram error: {e}")

    async def send_pushover(self, message):
        try:
            async with aiohttp.ClientSession() as session:
                await session.post("https://api.pushover.net/1/messages.json", data={
                    "token": self.pushover_token,
                    "user": self.pushover_user,
                    "title": "SkinBaron Update",
                    "message": message
                }, timeout=5)
        except Exception as e:
            logging.error(f"Pushover error: {e}")
