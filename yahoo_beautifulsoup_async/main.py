
import asyncio
from . import tasks

async def main_soup_async():
    task1 = asyncio.create_task(tasks.start_yahoo_scraper())

    await task1


if __name__ == '__main__':
    asyncio.run(main_soup_async())