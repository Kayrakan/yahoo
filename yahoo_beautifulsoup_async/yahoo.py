
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from . import config
import re
import pandas as pd
import numpy as np
import os
import io
from datetime import datetime


class YahooScraper():

    def __init__(self):

        self.xlsx_file_name= config.XLSX_FILE_NAME


    async def do_async_request(self,base_url, endpoint,headers={}, body={}, params={}, method="GET"):

        if method == "GET":
            url = f'{base_url}{endpoint}'
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url,headers= headers, params=params) as resp:
                        try:
                            if resp.status == 200:
                                print('200')
                                response = await resp.read()
                                return response
                            else:
                                if resp.status == 404:
                                    print('There is a problem with the request URL. Make sure that it is correct')
                                else:
                                    print('There was a problem retrieving data: ', resp.status)
                                return None
                        except Exception as e:
                            print(f'an error occured during the get request: {e}')
                            return None
            except asyncio.TimeoutError as e:
                print(e)
                return None

        elif method == "POST":
            url = f'{base_url}{endpoint}'
            print(url)

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url,headers= headers, data=body) as resp:
                        try:
                            if resp.status == 200:
                                response = await resp.read()
                                return response
                            else:
                                return None
                        except Exception as e:
                            print(f'an error occured during the post request: {e}')
                            return None
            except asyncio.TimeoutError:
                print('timeout error')
                return None


    def get_item_info(self,html_data, index=0):
        data_len = len(html_data)

        if  index >= data_len:
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


    async def scrape_currencies(self):

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}


        response = await self.do_async_request(base_url=config.BASE_URL, endpoint="/currencies", headers=headers, method="GET")

        soup = BeautifulSoup(response, 'html.parser')
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



    async def get_symbol_historical_data(self, symbol):
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


        url = f"/finance/download/{symbol}?period1={start_of_month}&period2={end_date}&interval=1d&events=history&includeAdjustedClose=true"

        headers = CaseInsensitiveDict()
        headers["authority"] = "query1.finance.yahoo.com"
        headers[
            "accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        headers["accept-language"] = "en-US;q=0.8"
        headers["referer"] = "https://finance.yahoo.com/quote/ZAR%3DX/history?p=ZAR%3DX"
        headers[
            "user-agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36"

        resp = await self.do_async_request("https://query1.finance.yahoo.com/v7", url, headers=headers) #requests.get(url, headers=headers)
        # resp = resp.content
        rawData = pd.read_csv(io.StringIO(resp.decode('utf-8')))
        print(rawData)
        csv_name = re.sub(r'[^a-zA-Z]', '', symbol)
        today = now.date().strftime("%Y_%m_%d")

        outdir = f'./Currencies/csv_{today}'
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        rawData.to_csv(f"{outdir}/{csv_name}.csv", encoding='utf-8')


    async def get_csv_five_top_currency(self, currencies):
        print(currencies)
        currencies = currencies.sort_values(by=['change_perc'], ascending=False)
        print(currencies)
        top_five_by_change_perc = currencies.head(5)
        print(top_five_by_change_perc)

        for symbol in list(top_five_by_change_perc['symbol']):

            await self.get_symbol_historical_data(symbol)