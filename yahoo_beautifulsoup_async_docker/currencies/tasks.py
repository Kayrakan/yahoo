
import asyncio
from yahoo import YahooScraper

async def start_yahoo_scraper():

    yahoo_instance = YahooScraper()

    scrape_task = asyncio.create_task(yahoo_instance.scrape_currencies())
    await scrape_task