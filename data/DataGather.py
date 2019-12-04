from bs4 import BeautifulSoup
import urllib
from urllib import parse, request
import requests
import pandas as pd
import sys
import os
from data import DataUtils
import time
import numpy as np
from sklearn import preprocessing
from datetime import date, timedelta
from multiprocessing import Pool


class _DataGather:
    stock_num = None
    raw_data_folder = None

    def __init__(self, stock_num):
        self.stock_num = stock_num
        self.raw_data_folder = DataUtils.get_raw_data_path()

    def get_stock_data_frame(self):
        file_path = self.raw_data_folder + '/' + self.stock_num + '.csv'
        if not os.path.exists(file_path):
            print('parse start: ', self.stock_num)
            df_stock_info = self.__get_stock_dataframe_from_web()
        else:
            now_time = time.time()
            modify_time = os.path.getmtime(file_path)
            if ((now_time - modify_time) > 60 * 60 * 12) or (time.gmtime(now_time).tm_hour > 9):
                print('update start: ', self.stock_num)
                df_stock_info = self.__update_stock_info()

            # if __is_need_update(stock_num):
            #     df_stock_info = __update_stock_info(stock_num)
            # else:
            #     df_stock_info = __get_stock_dataframe_from_csv(stock_num)
        df_stock_info['candle'] = (((df_stock_info['close'] - df_stock_info['open']) / df_stock_info['open']) * 100.0)
        # df_stock_info['candle'] = ((df_stock_info['close'] - df_stock_info['open']) > 0)

        # df_stock_info.loc[(df_stock_info['candle'] > 0), 'candle'] = 1
        # df_stock_info.loc[(df_stock_info['candle'] < 0), 'candle'] = -1
        df_stock_info['candle_diff'] = ((df_stock_info['close'] - df_stock_info['open']) > 0)
        df_stock_info['volume'] = df_stock_info['close'] * df_stock_info['volume']
        return df_stock_info

    def __get_stock_dataframe_from_web(self):
        global stock_info
        global stock_demand

        stock_info = []
        stock_demand = []
        last_page_num = self.__get_last_page_num_demand()
        count = 0
        for page_num in range(1, (last_page_num * 2)):
            self.__parse_stock_info(str(page_num))
            count += 1
        #         std_print_overwrite('Parsing Progress: ' + str(round(float((count * 100.0) / max_page_num), 1)) + ' %')
        for page_num in range(1, last_page_num):
            self.__parse_stock_demand(str(page_num))
            count += 1
        #         std_print_overwrite('Parsing Progress: ' + str(round(float((count * 100.0) / max_page_num), 1)) + ' %')
        df_info = pd.DataFrame(stock_info)
        df_demand = pd.DataFrame(stock_demand)
        df_info.set_index(0, inplace=True)
        df_demand.set_index(0, inplace=True)

        print(self.stock_num, ': ', df_info.shape, ', ', df_demand.shape)
        if df_info.shape[0] != df_demand.shape[0]:
            df_info = df_info[:df_demand.shape[0]]
        df = pd.concat([df_info, df_demand], axis=1)
        df.sort_index(inplace=True, ascending=False)
        df = df.dropna()
        df.columns = ['close', 'diff', 'open', 'high', 'low', 'volume', 'agency', 'foreign']
        df.to_csv(self.raw_data_folder + '/' + self.stock_num + '.csv')
        return df

    def __get_stock_dataframe_from_csv(self):
        df = pd.read_csv(self.raw_data_folder + '/' + self.stock_num + '.csv', index_col=0)
        return df

    def __update_stock_info(self):
        global stock_info
        global stock_demand

        stock_info = []
        stock_demand = []
        df_csv = self.__get_stock_dataframe_from_csv()
        self.__parse_stock_info('1')
        self.__parse_stock_info('2')
        self.__parse_stock_demand('1')
        df_info = pd.DataFrame(stock_info)
        df_demand = pd.DataFrame(stock_demand)
        df_info.set_index(0, inplace=True)
        df_demand.set_index(0, inplace=True)
        df_update = (pd.concat([df_info, df_demand], axis=1)).sort_index(ascending=False)
        df_update.columns = ['close', 'diff', 'open', 'high', 'low', 'volume', 'agency', 'foreign']
        df_result = df_csv.combine_first(df_update)
        df_result.sort_index(inplace=True, ascending=False)
        df_result.to_csv(self.raw_data_folder + '/' + self.stock_num + '.csv')
        return df_result

    def __parse_stock_demand(self, page_num):
        global stock_demand
        # parse index- day | agency | foreign
        parse_url = 'http://finance.naver.com/item/frgn.nhn?code=' + self.stock_num + '&page=' + page_num
        soup = BeautifulSoup(request.urlopen(parse_url), 'lxml')
        elements = soup.findAll('tr', {'onmouseover': 'mouseOver(this)'})

        for element in elements:
            demand = []
            text_array = element.text.split()
            for idx in range(len(text_array)):
                if idx % 9 == 0: demand.append(text_array[idx])
                if idx % 9 == 5: demand.append(float(text_array[idx].replace(',', '')) / 1000.)
                if idx % 9 == 6: demand.append(float(text_array[idx].replace(',', '')) / 1000.)
            stock_demand.append(demand)

    def __parse_stock_info(self, page_num):
        global stock_info
        # parse index- end | diff | open | high | low | volume
        parse_url = 'http://finance.naver.com/item/sise_day.nhn?code=' + self.stock_num + '&page=' + page_num
        soup = BeautifulSoup(request.urlopen(parse_url), 'lxml')
        elements_day = soup.findAll('td', {'align': 'center'})
        elements_num = soup.findAll('td', {'class': 'num'})

        count = 0
        diff = 1
        for elements in elements_day:
            info = []
            day = elements.text
            info.append(day)
            for idx in range(6):
                idx += (count * 6)
                if len(elements_num[idx].text) == 1:
                    continue
                parse_value = int(elements_num[idx].text.replace(',', ''))
                if idx % 6 == 1:
                    if parse_value == 0:
                        diff = 0
                    elif 'ico_down.gif' in elements_num[idx].img['src']:
                        # elif elements_num[idx].img['src'] == 'http://imgstock.naver.com/images/images4/ico_down.gif':
                        diff = -1
                parsed_info = diff * int(elements_num[idx].text.replace(',', ''))
                info.append(parsed_info)
                diff = 1
            count += 1
            stock_info.append(info)

    # def __get_last_day_from_web(stock_num):
    #     parse_url = 'http://finance.naver.com/item/frgn.nhn?code=' + stock_num
    #     #     soup = BeautifulSoup(urllib.request.urlopen(parse_url), 'lxml')
    #     soup = BeautifulSoup(urllib.urlopen(parse_url), 'lxml')
    #     elements = soup.findAll('tr', {'onmouseover': 'mouseOver(this)'})
    #     return elements[0].text.split()[0]


    # def __get_last_page_num_info(stock_num):
    #     content = requests.get(('http://finance.naver.com/item/frgn.nhn?code=' + stock_num)).text
    #     soup = BeautifulSoup(content)
    #     return __get_last_page(soup)

    def __get_last_page_num_demand(self):
        content = requests.get(('http://finance.naver.com/item/frgn.nhn?code=' + self.stock_num)).text
        soup = BeautifulSoup(content, features='lxml')
        return self.__get_last_page(soup)

    def __get_last_page(self, soup):
        pgrrs = soup.findAll('td', {'class': 'pgRR'})
        parsed = parse.urlparse(pgrrs[0].a['href'])
        parsed_qs = parse.parse_qs(parsed.query, keep_blank_values=True)
        return int(parsed_qs['page'][0])

    # def __get_today_open(stock_num):
    #     parse_url = 'http://finance.naver.com/item/main.nhn?code=' + stock_num
    #     #     soup = BeautifulSoup(urllib.request.urlopen(parse_url), 'lxml')
    #     soup = BeautifulSoup(request.urlopen(parse_url), 'lxml')
    #     elements = soup.findAll('dd')
    #     today_open = float(elements[5].text.split()[1].replace(',', ''))
    #     print('today open: ', today_open)
    #     return today_open

    # def __get_yesterday_string():
    #     yesterday = date.today() - timedelta(1)
    #     return yesterday.strftime('%Y.%m.%d')

    def get_stock_dataset(self):
        df_stock_info = None
        return pd.read_csv(os.path.join(self.raw_data_folder, self.stock_num + '.csv'))

