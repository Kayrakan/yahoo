
from yahoo_beautifulsoup.main import main_soup
from yahoo_beautifulsoup_async.main import main_soup_async

import asyncio


import os

from scrapy.crawler import CrawlerProcess
from yahoo_scrapy.yahooscraper.spiders import yahoospider
from yahoo_scrapy.yahooscraper import settings
from scrapy.settings import Settings
import click


import sys

def run_scrapy():

    sys.path.append(os.path.abspath("./yahoo_scrapy/"))
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(yahoospider.YahooSpider)
    process.start()

def run_soup_async():

    asyncio.run(main_soup_async())


SCRAPERS = {
    "soup" : main_soup,
    "scrapy": run_scrapy,
    "soup_async": run_soup_async
}


@click.command()
@click.option("--method", type=click.Choice(SCRAPERS.keys()), default="soup", help="Choose scraper method")
def main(method):
    if method in SCRAPERS.keys():
        SCRAPERS[method]()
    else:
        print(f'cant find the method: {method}. method should be one of the following:')
        for m in SCRAPERS:
            print(m)


if __name__ == '__main__':
    main()