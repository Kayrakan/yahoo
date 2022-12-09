
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import config
import re
import pandas as pd
import numpy as np

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



    def load_excel_from_pd(self,df):

        total_columns = len(df.columns) - 1  # minus 1 since index is zero

        total_rows = df.shape[0]
        df['change_perc'] = df.change_perc.replace('', np.nan).astype(float)
        writer = pd.ExcelWriter(self.xlsx_file_name, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        worksheet.conditional_format(1, total_columns, total_rows, total_columns, {'type': '3_color_scale',
                                                                                   'min_color': 'red',
                                                                                   'mid_color': 'yellow',
                                                                                   'max_color': 'green'
                                                                                   })
        writer.save()

        import time
        while True:
            time.sleep(1)

