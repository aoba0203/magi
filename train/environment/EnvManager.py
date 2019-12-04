import os
import pandas as pd
import numpy as np
import asyncio
from data import DataManager, DataUtils, DayUtils
from pprint import pprint
from train.environment.EnvBase import EnvBase


NUMBER_OF_BUYING_STOCKS = 5


# class Stock:
#     DataManager = None
#     name = None
#     num = None
#     count = None
#     queue_sell = None
#     stock_df = None
#
#     def __init__(self, _stock_num):
#         self.DataManager = DataManager.DataManager(_stock_num)
#         self.name = DataUtils.get_stock_num_to_name(_stock_num)
#         self.num = _stock_num
#         self.queue_sell = asyncio.Queue()
#         self.stock_df = self.DataManager.get_dataframe()
#
#     def buy(self, count_buying):
#         self.count += count_buying
#         self.make_sell_queue()
#         return count_buying
#
#     def sell(self):
#         try:
#             count_selling = self.queue_sell.get_nowait()
#         except asyncio.QueueEmpty:
#             count_selling = 0
#
#         self.count -= count_selling
#         return count_selling, self.queue_sell.empty()
#
#     def make_sell_queue(self):
#         self.queue_sell = asyncio.Queue()
#         first_count = int(self.count * 0.3)
#         second_count = int(self.count * 0.3)
#         third_count = self.count - (first_count + second_count)
#         self.queue_sell.put(first_count)
#         self.queue_sell.put(second_count)
#         self.queue_sell.put(third_count)

    # def get_evaluation_amount(self, day):
    #     evaluation_price = DataManager.get_day_close_price(self.stock_df, day, DataManager.DIFF_DAY_TODAY)
    #     return self.count * evaluation_price
    #
    # def get_price_tomorrow_open(self, day):
    #     return DataManager.get_day_close_price(self.stock_df, day, DataManager.DIFF_DAY_TOMORROW)
    #
    # def get_price_today_close(self, day):
    #     return DataManager.get_day_close_price(self.stock_df, day, DataManager.DIFF_DAY_TODAY)
    #
    # def get_stock_count(self):
    #     return self.count


class StockEnv:
    stock_num = None
    df = None

    def __init__(self, stock_num):
        self.stock_num = stock_num
        self.df = DataManager.get_stock_data_frame(self.stock_num)

    def get_price_volatility(self, day):
        return DataManager.get_day_volatility(self.df, day)

    def get_foreign_demand(self, day):
        return DataManager.get_day_demand_foreign(self.df, day)

    def get_agency_demand(self, day):
        return DataManager.get_day_demand_agency(self.df, day)


class AccountEnv:
    estimated_account = None
    budget_init = None
    budget_remain = None
    budget_buying_per_stock = None
    dic_stock_on_hands = None

    # class Stock:
    def __new__(cls, budget=50000000):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AccountEnv, cls).__new__(cls, budget)
        cls.estimated_account = 0
        cls.budget_init = budget
        cls.budget_remain = budget
        cls.budget_buying_per_stock = budget / (NUMBER_OF_BUYING_STOCKS * 5)
        cls.dic_stock_on_hands = {}
        return cls.instance

    def initialize(self, budget=50000000):
        self.estimated_account = 0
        self.budget_init = budget
        self.budget_remain = budget
        self.budget_buying_per_stock = budget / (NUMBER_OF_BUYING_STOCKS * 5)
        self.dic_stock_on_hands = {}

    # def __init__(self, budget=50000000):
    #     self.estimated_account = 0
    #     self.budget_init = budget
    #     self.budget_remain = budget
    #     self.budget_buying_per_stock = budget / (NUMBER_OF_BUYING_STOCKS * 5)
    #     self.dic_stock_on_hands = {}

    def buy_stock(self, day, stock_num):
        if stock_num not in self.dic_stock_on_hands:
            self.dic_stock_on_hands[stock_num] = Stock(stock_num)
        stock = self.dic_stock_on_hands[stock_num]
        purchase_price = stock.get_price_tomorrow_open(day)
        purchase_count = int(self.budget_buying_per_stock / purchase_price)
        purchase_amount = purchase_price * purchase_count
        if purchase_amount > self.budget_remain:
            print("Can't buy the stock: " + str(stock_num) + ', Amount: ' + str(purchase_amount) + ", Remain: " + str(self.budget_remain))
        else:
            self.budget_remain -= purchase_amount
            stock.buy(purchase_count)
            self.dic_stock_on_hands[stock_num] = stock

    def sell_stock(self, day, stock_num):
        if stock_num not in self.dic_stock_on_hands.keys():
            return
        stock = self.dic_stock_on_hands[stock_num]
        sell_price = stock.get_price_tomorrow_open(day)
        sell_count, empty = stock.sell()
        sell_amount = sell_price * sell_count
        self.budget_remain += sell_amount
        self.dic_stock_on_hands[stock_num] = stock
        if empty:
            del self.dic_stock_on_hands[stock_num]

    def get_estimated_account(self, day):
        account_amount = self.budget_remain
        for key in self.dic_stock_on_hands.keys():
            stock = self.dic_stock_on_hands[key]
            stock_price = stock.get_price_today_close(day)
            stock_count = stock.get_stock_count()
            stock_amount = stock_price * stock_count
            account_amount += stock_amount
        return account_amount

    def get_init_budget(self):
        return self.budget_init

    def print_account_state(self):
        pprint(self.dic_stock_on_hands)


class EnvPrice(EnvBase):

    def step(self, action_buys, action_sells):
        rewards = 0
        states = []
        return rewards, states


class EnvManager:
    DataManager = None
    stock_num = None
    stock = None
    account = None
    day_list = None
    day_idx = 0

    def __init__(self, _stock_num, _target_month, _budget=50000000):
        self.account = AccountEnv(_budget)
        self.stock_num = _stock_num
        self.DataManager = DataManager.DataManager(self.stock_num)
        self.day_list = self.DataManager.get_daylist_in_month(_target_month)
        self.day_idx = 0

    def step_price(self, action_buy_stock_list, action_sell_stock_list):
        done = False
        day_target = self.day_list[self.day_idx]
        for buy_stock in action_buy_stock_list:
            self.account.buy_stock(day_target, buy_stock)
        for sell_stock in action_sell_stock_list:
            self.account.sell_stock(day_target, sell_stock)

        self.day_idx += 1
        if self.day_idx > len(self.day_list):
            done = True
            self.day_idx -= 1
        rewards = self.account.get_estimated_account(day_target)
        return rewards, self.day_list[self.day_idx], done


