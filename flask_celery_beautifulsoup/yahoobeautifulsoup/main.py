
import asyncio

from yahoobeautifulsoup import tasks

async def main(file_name):
    task1 = asyncio.create_task(tasks.start_yahoo_scraper(file_name))
    name = await task1

    return name


def async_scraper(file_name):

    name = asyncio.run(main(file_name))
    return name