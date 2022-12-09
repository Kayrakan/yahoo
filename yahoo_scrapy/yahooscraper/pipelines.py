# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import xlsxwriter
from datetime import datetime
import os

class YahooscraperPipeline:

    @classmethod
    def from_crawler(cls, crawler):
        file_name = crawler.settings.get('XLSX_FILE')
        return cls(xlsx_name=file_name)

    def __init__(self, xlsx_name):

        self.xlsx_name = xlsx_name
        self.workbook = None
        self.worksheet = None
        self.current_row_index = 0
        self.current_column_index = 0

        self.scraped_data = []

        self.first_row = 1
        self.first_column = None
        self.last_row = None
        self.last_column = None

    def process_item(self, item, spider):
        spider.logger.info('ITEM IS PROCESSED')
        item_dict = ItemAdapter(item).asdict()


        if self.current_row_index == 0:

            data = item_dict.keys()
        else:
            data = item_dict.values()

        for (col, value) in enumerate(data):

            if self.current_row_index != 0 and (col <= (len(data)-1) and col >= (len(data)-3)):
                value = float(value)
            self.worksheet.write(self.current_row_index, col, value)

        self.current_row_index += 1
        self.scraped_data.append(item)
        return item

    def open_spider(self, spider):
        spider.logger.info('SPIDER IS OPEN')

        today = datetime.today().date().strftime("%Y_%m_%d")
        outdir = f'./Currencies'
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        self.workbook = xlsxwriter.Workbook(f"{outdir}/{self.xlsx_name}_{today}.xlsx")
        self.worksheet = self.workbook.add_worksheet()

    def close_spider(self, spider):

        total_rows = len(self.scraped_data)
        total_columns = len(self.scraped_data[0])-1 # minus 1 since column index zero

        #last row color scaled
        self.worksheet.conditional_format(1, total_columns, total_rows, total_columns, {'type': '3_color_scale',
                                                            'min_color': 'red',
                                                            'mid_color': 'yellow',
                                                            'max_color': 'green'
                                                        })
        spider.logger.info('SPIDER IS CLOSED')

        self.workbook.close()

