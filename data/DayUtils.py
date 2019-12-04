import numpy as np
from data import DataUtils
import pandas as pd

DIFF_DAY_TOMORROW = -1
DIFF_DAY_TODAY = 0

DEFAULT_STOCK_NUM = '066570'
stock_df = None


class DayUtils:
    stock_df = None
    DataProcessor = None

    def __init__(self, _stock_df):
        # self.DataProcessor = DataProcessor.DataProcessor(stock_num)
        self.stock_df = _stock_df

    def get_day_open_price(self, _day, _diff_day):
        # df = get_stock_data_frame(stock_num)
        price_open = self.stock_df.iloc[(np.where(self.stock_df.index.values == _day)[0][0]) - _diff_day]['open']
        return price_open

    def get_day_close_price(self, _day, _diff_day):
        # df = get_stock_data_frame(stock_num)
        price_close = self.stock_df.iloc[(np.where(self.stock_df.index.values == _day)[0][0]) - _diff_day]['close']
        return price_close

    def get_day_volatility(self, _day):
        # df = get_stock_data_frame(stock_num)
        position_today = np.where(self.stock_df.index.values == _day)[0][0]
        volatility = self.stock_df.iloc[position_today - DIFF_DAY_TODAY]['percent']
        return volatility

    def get_day_demand_foreign(self, _day):
        # df = get_stock_data_frame(stock_num)
        position_today = np.where(self.stock_df.index.values == _day)[0][0]
        demand_foreign = self.stock_df.iloc[position_today - DIFF_DAY_TODAY]['foreign']
        return demand_foreign

    def get_day_demand_agency(self, _day):
        # df = get_stock_data_frame(stock_num)
        position_today = np.where(self.stock_df.index.values == _day)[0][0]
        demand_agency = self.stock_df.iloc[position_today - DIFF_DAY_TODAY]['agency']
        return demand_agency


def get_month_list(_stock_num):
    stock_dataframe = DataUtils.get_stock_df(_stock_num)
    day_end = stock_dataframe.index[0]
    day_start = stock_dataframe.index[-1]
    return pd.date_range(day_start, day_end, freq='MS').strftime('%Y.%m').tolist()
