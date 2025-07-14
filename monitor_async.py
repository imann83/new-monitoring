
import aiohttp
import asyncio
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from notifier_async import AsyncNotifier

class AsyncSkinBaronMonitor:
    def __init__(self, url, check_interval=1):
        self.url = url
        self.check_interval = check_interval
        self.notifier = AsyncNotifier()
        self.previous_signatures = set()
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "text/html",
                "Accept-Language": "en-US,en;q=0.5"
            }
        )
        self.status = {
            "is_running": False,
            "start_time": None,
            "last_check": None,
            "total_checks": 0,
            "last_error": None
        }

    async def fetch_page(self):
        try:
            async with self.session.get(self.url, timeout=10) as response:
                html = await response.text()
                return BeautifulSoup(html, "html.parser")
        except Exception as e:
            logging.error(f"Fetch error: {e}")
            self.status["last_error"] = str(e)
            return None

    async def extract_products(self, soup):
        selectors = ['.item-card', '.product-item', '[data-item-id]']
        for selector in selectors:
            elements = soup.select(selector)
            if elements and len(elements) >= 1:
                return elements[:10]
        return []

    def make_signature(self, element):
        text = element.get_text(strip=True)
        return hash(text)

    async def check_for_changes(self):
        soup = await self.fetch_page()
        if not soup:
            return
        elements = await self.extract_products(soup)
        if not elements:
            logging.warning("No products extracted.")
            return
        signatures = set(self.make_signature(el) for el in elements)
        if not self.previous_signatures:
            self.previous_signatures = signatures
            return
        if signatures != self.previous_signatures:
            diff = len(signatures.symmetric_difference(self.previous_signatures))
            logging.info(f"{diff} change(s) detected.")
            await self.notifier.send(f"🔔 Change detected at {datetime.now().strftime('%H:%M:%S')}")
            self.previous_signatures = signatures

    async def run(self):
        self.status["is_running"] = True
        self.status["start_time"] = datetime.now()
        logging.info("Monitor started.")
        await self.notifier.send("🚀 Async SkinBaron monitor started.")
        while self.status["is_running"]:
            try:
                await self.check_for_changes()
                self.status["last_check"] = datetime.now()
                self.status["total_checks"] += 1
            except Exception as e:
                self.status["last_error"] = str(e)
                logging.error(f"Error in loop: {e}")
            await asyncio.sleep(self.check_interval)

    async def close(self):
        await self.session.close()
