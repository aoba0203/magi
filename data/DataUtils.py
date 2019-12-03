from bs4 import BeautifulSoup
import csv
import os
import re
import requests
from data import DataGather


mStock_num_dic = {}
mStock_name_dic = {}


def parse_stock_dictionary():
    global mStock_num_dic
    global mStock_name_dic

    base_url_kospi = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok=0&page='
    base_url_kosdaq = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok=1&page='

    mStock_num_dic = {}
    mStock_name_dic = {}
    for base_url in [base_url_kospi, base_url_kosdaq]:
        for i in range(1, 11):
            url = base_url + str(i)
            r = requests.get(url)

            soup = BeautifulSoup(r.text, 'lxml')
            t_items = soup.find_all('tr', {'onmouseover': 'mouseOver(this)'})
            for item in t_items:
                txt = item.a.get('href')
                k = re.search('[\d]', txt)
                if k:
                    code = str(txt.split('=')[1])
                    name = item.find_all('a', {'class': 'tltle'})[0].text
                    mStock_num_dic[code] = name
                    mStock_name_dic[name] = code


def get_stock_num_to_name(_stock_num):
    global mStock_num_dic
    if len(mStock_num_dic) < 1000:
        parse_stock_dictionary()
    return mStock_num_dic[_stock_num]


def get_stock_name_to_num(_stock_name):
    global mStock_name_dic
    if len(mStock_name_dic) < 1000:
        parse_stock_dictionary()
    return mStock_name_dic[_stock_name]


def write_dictionary_to_csv(dictionary, csv_file_name):
    try:
        with open(csv_file_name, 'w') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in dictionary.items():
                writer.writerow([key, value])
    except IOError:
        print('expect')


def read_dictionary_to_csv(csv_file_name):
    stock_dict = {}
    try:
        with open(csv_file_name, 'r') as csv_file:
            reader = csv.reader(csv_file)
            for rows in reader:
                print(rows)

            stock_dict = {rows[0]: rows[1] for rows in reader}
    except IOError:
        print('expect')
    return stock_dict


def get_stock_df_to_csv(_stock_num):
    data_gather = DataGather._DataGather(_stock_num)
    return data_gather.get_stock_data_frame()


def get_raw_data_path():
    paths = os.getcwd() + '/raw_data/'
    if not os.path.exists(paths):
        os.makedirs(paths)
    return paths


def get_chart_data_path():
    paths = os.getcwd() + '/chart_data'
    if not os.path.exists(paths):
        os.makedirs(paths)
    return paths
