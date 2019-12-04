import abc
from data import DataManager
from data import DataUtils
import asyncio
import numpy as np


NUMBER_OF_BUYING_STOCKS = 5
DIFF_DAY_TOMORROW = -1
DIFF_DAY_TODAY = 0


class _Stock:
    DataManager = None
    name = None
    num = None
    count = None
    queue_sell = None
    stock_df = None
    amount_foreign = None
    amount_agency = None

    def __init__(self, _stock_num):
        self.DataManager = DataManager.DataManager(_stock_num)
        self.name = DataUtils.get_stock_num_to_name(_stock_num)
        self.num = _stock_num
        self.queue_sell = asyncio.Queue()
        self.stock_df = self.DataManager.get_dataframe()
        self.count = 0
        self.amount_foreign = 0
        self.amount_agency = 0

    def buy(self, count_buying):
        self.count += count_buying
        self.make_sell_queue()
        return count_buying

    def sell(self):
        try:
            count_selling = self.queue_sell.get_nowait()
        except asyncio.QueueEmpty:
            count_selling = 0

        self.count -= count_selling
        return count_selling, self.queue_sell.empty()

    def make_sell_queue(self):
        self.queue_sell = asyncio.Queue()
        first_count = int(self.count * 0.3)
        second_count = int(self.count * 0.3)
        third_count = self.count - (first_count + second_count)
        self.queue_sell.put(first_count)
        self.queue_sell.put(second_count)
        self.queue_sell.put(third_count)

    def buy_foreign(self, amount):
        self.amount_foreign += amount

    def sell_foreign(self, amount):
        self.amount_foreign -= amount

    def get_foreign(self):
        return self.amount_foreign

    def buy_agency(self, amount):
        self.amount_agency += amount

    def sell_agency(self, amount):
        self.amount_agency -= amount

    def get_agency(self):
        return self.amount_agency

    def get_day_open_price(self, _day, _diff_day):
        price_open = self.stock_df.iloc[(np.where(self.stock_df.index.values == _day)[0][0]) - _diff_day]['open']
        return price_open

    def get_day_close_price(self, _day, _diff_day):
        price_close = self.stock_df.iloc[(np.where(self.stock_df.index.values == _day)[0][0]) - _diff_day]['close']
        return price_close

    def get_day_volatility(self, _day):
        position_today = np.where(self.stock_df.index.values == _day)[0][0]
        volatility = self.stock_df.iloc[position_today - DIFF_DAY_TODAY]['percent']
        return float(volatility)

    def get_day_demand_foreign(self, _day):
        position_today = np.where(self.stock_df.index.values == _day)[0][0]
        demand_foreign = self.stock_df.iloc[position_today - DIFF_DAY_TODAY]['foreign']
        return float(demand_foreign)

    def get_day_demand_agency(self, _day):
        position_today = np.where(self.stock_df.index.values == _day)[0][0]
        demand_agency = self.stock_df.iloc[position_today - DIFF_DAY_TODAY]['agency']
        return float(demand_agency)

    def get_stock_count(self):
        return self.count

    def __str__(self):
        return self.name + ', Hold: ' + str(self.count)


class _AccountEnv(object):
    global NUMBER_OF_BUYING_STOCKS

    _instance = None
    estimated_account = None
    budget_init = None
    budget_remain = None
    budget_buying_per_stock = None
    dic_stock_on_hands = None

    # def __new__(cls, budget=50000000):
    #     if not isinstance(cls._instance, cls):
    #         cls._instance = object.__new__(cls)
    #     cls.estimated_account = 0
    #     cls.budget_init = budget
    #     cls.budget_remain = budget
    #     cls.budget_buying_per_stock = budget / (NUMBER_OF_BUYING_STOCKS * 5)
    #     cls.dic_stock_on_hands = {}
    #     return cls._instance

    def __init__(self, budget=50000000):
        self.estimated_account = 0
        self.budget_init = budget
        self.budget_remain = budget
        self.budget_buying_per_stock = budget / (NUMBER_OF_BUYING_STOCKS * 5)
        self.dic_stock_on_hands = {}

    def initialize(self, budget=50000000):
        self.estimated_account = 0
        self.budget_init = budget
        self.budget_remain = budget
        self.budget_buying_per_stock = budget / (NUMBER_OF_BUYING_STOCKS * 5)
        self.dic_stock_on_hands = {}

    @abc.abstractmethod
    def buy_stock(self, day, stock_num):
        pass

    @abc.abstractmethod
    def sell_stock(self, day, stock_num):
        pass

    @abc.abstractmethod
    def get_estimated_account(self, day):
        pass

    @abc.abstractmethod
    def get_init_budget(self):
        pass

    def print_account_state(self, day):
        for key in self.dic_stock_on_hands.keys():
            print(key, self.dic_stock_on_hands[key])
        print('Account: ', self.get_estimated_account(day))


class EnvBase:
    __metaclass = abc.ABCMeta
    DataManager = None
    stock_num = None
    stock = None
    account = None
    day_list = None
    day_idx = 0

    def __init__(self, _stock_num, _target_month, _budget=50000000):
        self.account = _AccountEnv(_budget)
        self.stock_num = _stock_num
        self.DataManager = DataManager.DataManager(self.stock_num)
        self.day_list = self.DataManager.get_daylist_in_month(_target_month)
        self.day_idx = 0

    @abc.abstractmethod
    def set_account(self):
        pass

    @abc.abstractmethod
    def step(self, action_buys, action_sells):
        pass
