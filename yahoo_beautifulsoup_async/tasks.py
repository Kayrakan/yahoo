
import asyncio
from .yahoo import YahooScraper

async def start_yahoo_scraper():

    yahoo_instance = YahooScraper()

    currencies =  await asyncio.create_task(yahoo_instance.scrape_currencies())

    top_currencies_to_csv = asyncio.create_task(yahoo_instance.get_csv_five_top_currency(currencies))
    await top_currencies_to_csv