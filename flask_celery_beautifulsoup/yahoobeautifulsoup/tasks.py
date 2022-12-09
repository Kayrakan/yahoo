
import asyncio
import config
from yahoobeautifulsoup.yahoo import YahooScraper

async def start_yahoo_scraper(filename):

    yahoo_instance = YahooScraper()

    scrape_task = asyncio.create_task(yahoo_instance.scrape_currencies(filename))
    return await scrape_task