
import requests
from bs4 import BeautifulSoup
from . import config
import re
import pandas as pd
import numpy as np
import io
import os
from datetime import datetime
import re

class YahooScraper():

    def __init__(self, session=None):
        self.session = requests.Session() if session is None else session
        self.xlsx_file_name= config.XLSX_FILE_NAME
        self.base_url = config.BASE_URL
        self.currencies_url = config.CURRENCIES

    def do_request(self, path=None, method="GET", params=None, headers=None, payload=None):

        if method == "POST":
            try:
                response = self.session.post(

                    path, data=payload, headers=headers,
                )
                response.raise_for_status()
            except requests.exceptions.HTTPError as errh:
                return errh.response
            except requests.exceptions.ConnectionError as errc:
                print(errc.response)
                return errc.response
            except requests.exceptions.Timeout as errt:
                return errt.response
            except requests.exceptions.RequestException as err:
                return err.response

        else:
            try:
                response = self.session.get(

                    path, headers=self.session.headers, params=params
                )
                response.raise_for_status()
            except requests.exceptions.HTTPError as errh:
                return errh.response
            except requests.exceptions.ConnectionError as errc:
                return errc.response
            except requests.exceptions.Timeout as errt:
                return errt.response
            except requests.exceptions.RequestException as err:
                return err.response

        return response

    def get_item_info(self, html_data, index=0):
        data_len = len(html_data)

        if index >= data_len:
            return

        else:
            last_price = html_data[index].find("td", {'aria-label': 'Last Price'}).text.replace(',', '.')
            yield {
                "symbol" : html_data[index].find("td", {'aria-label':'Symbol'}).text,
                "name" : html_data[index].find("td", {'aria-label':'Name'}).text,
                "last_price" : last_price.replace('.', '', last_price.count('.') - 1),
                "change" : html_data[index].find("td", {'aria-label':'Change'}).text.replace('+',''),
                "change_perc" :  re.subn('[+%]', '', html_data[index].find("td", {'aria-label':'% Change'}).text)[0]
            }
        index += 1
        yield from self.get_item_info(html_data,index= index )


    def scrape_currencies(self):

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}

        response = self.do_request(path=config.BASE_URL + self.currencies_url,  method="GET", headers=headers)
        print(response)
        soup = BeautifulSoup(response.content, 'html.parser')
        currencies = pd.DataFrame()

        for item in self.get_item_info(soup.select('.simpTblRow')):
            df_dictionary = pd.DataFrame([item])
            currencies = pd.concat([currencies, df_dictionary], ignore_index=True)


        self.load_excel_from_pd(currencies)

        return currencies



    def load_excel_from_pd(self,df):

        total_columns = len(df.columns) - 1  # minus 1 since index is zero

        total_rows = df.shape[0]
        df['change_perc'] = df.change_perc.replace('', np.nan).astype(float)

        today = datetime.today().date().strftime("%Y_%m_%d")
        outdir = f'./Currencies'
        if not os.path.exists(outdir):
            os.mkdir(outdir)

        writer = pd.ExcelWriter(f"{outdir}/{self.xlsx_file_name}_{today}.xlsx", engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        worksheet.conditional_format(1, total_columns, total_rows, total_columns, {'type': '3_color_scale',
                                                                                   'min_color': 'red',
                                                                                   'mid_color': 'yellow',
                                                                                   'max_color': 'green'
                                                                                   })
        writer.save()


    def get_symbol_historical_data(self, symbol):
        import requests
        from requests.structures import CaseInsensitiveDict

        now = datetime.today()
        print(f'now : {now}')
        start_of_month = now.replace(day=1)
        print(f"start {start_of_month}")
        end_date = now.strftime('%s')
        print(f'now : {now}')
        start_of_month = start_of_month.strftime('%s')
        print(f"start {start_of_month}")


        url = f"https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={start_of_month}&period2={end_date}&interval=1d&events=history&includeAdjustedClose=true"

        headers = CaseInsensitiveDict()
        headers["authority"] = "query1.finance.yahoo.com"
        headers[
            "accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        headers["accept-language"] = "en-US;q=0.8"
        headers["referer"] = "https://finance.yahoo.com/quote/ZAR%3DX/history?p=ZAR%3DX"
        headers[
            "user-agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36"

        resp = requests.get(url, headers=headers)
        resp = resp.content
        rawData = pd.read_csv(io.StringIO(resp.decode('utf-8')))
        print(rawData)
        csv_name = re.sub(r'[^a-zA-Z]', '', symbol)
        today = now.date().strftime("%Y_%m_%d")

        outdir = f'./Currencies/csv_{today}'
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        rawData.to_csv(f"{outdir}/{csv_name}.csv", encoding='utf-8')

    def get_csv_five_top_currency(self, currencies):

        print(currencies)
        currencies = currencies.sort_values(by=['change_perc'], ascending=False)
        print(currencies)
        top_five_by_change_perc = currencies.head(5)
        print(top_five_by_change_perc)

        for symbol in list(top_five_by_change_perc['symbol']):

            self.get_symbol_historical_data(symbol)

