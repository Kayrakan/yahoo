
from .yahoo import YahooScraper

def start_yahoo_scraper():

    yahoo_instance = YahooScraper()

    currencies = yahoo_instance.scrape_currencies()

    yahoo_instance.get_csv_five_top_currency(currencies)
