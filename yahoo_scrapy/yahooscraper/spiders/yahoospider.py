import scrapy
import re


class YahooSpider(scrapy.Spider):
    name = "currencies"
    start_urls = ['https://finance.yahoo.com/currencies']

    def parse(self, response):

        for currency_pair in response.css('.simpTblRow'):
            try:
                last_price = currency_pair.css("td[aria-label = 'Last Price'] fin-streamer::text").get().replace(',','.')

                yield {
                    "symbol": currency_pair.css("td[aria-label = 'Symbol'] a::text").get(),
                    "name": currency_pair.css("td[aria-label = 'Name']::text").get(),
                    "last_price": last_price.replace('.', '', last_price.count('.') - 1),
                    "change": currency_pair.css("td[aria-label = 'Change'] fin-streamer span::text").get().replace('+',''),
                    "%change":  re.subn('[+%]', '',  currency_pair.css("td[aria-label = '% Change'] fin-streamer span::text").get())[0],
                }

            except Exception as e:
                print(f'an error occured during yielding the pair data: {e}')
