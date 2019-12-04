from train.environment.EnvBase import EnvBase, _AccountEnv, _Stock
from train.environment import EnvBase as Env
from data import DataManager


class ForeignAccount(_AccountEnv):
    def buy_stock(self, day, stock_num):
        if stock_num not in self.dic_stock_on_hands:
            self.dic_stock_on_hands[stock_num] = _Stock(stock_num)
        stock = self.dic_stock_on_hands[stock_num]
        buy_price = stock.get_day_open_price(day, Env.DIFF_DAY_TOMORROW)
        buy_foreign = stock.get_day_demand_foreign(day)
        buy_count = int(self.budget_buying_per_stock / buy_price)
        buy_amount = buy_count * buy_price
        if buy_amount > self.budget_remain:
            print("Can't buy the stock: " + str(stock_num) + ', Amount: ' + str(buy_amount) + ", Remain: " + str(self.budget_remain))
        else:
            self.budget_remain -= buy_amount
            stock.buy(buy_count)
            self.dic_stock_on_hands[stock_num] = stock
            stock.buy_foreign(buy_foreign * buy_count)

    def sell_stock(self, day, stock_num):
        if stock_num not in self.dic_stock_on_hands.keys():
            return
        stock = self.dic_stock_on_hands[stock_num]
        sell_foreign = stock.get_day_demand_foreign(day)
        sell_count, empty = stock.sell()
        sell_amount = sell_foreign * sell_count
        self.budget_remain += sell_amount
        self.dic_stock_on_hands[stock_num] = stock
        sell_foreign = stock.get_day_demand_agency(day)
        stock.sell_foreign(sell_foreign * sell_count)
        if empty:
            del self.dic_stock_on_hands[stock_num]

    def get_estimated_account(self, day):
        account_amount = self.budget_remain
        account_foreign = 0
        for key in self.dic_stock_on_hands.keys():
            stock = self.dic_stock_on_hands[key]
            stock_price = stock.get_day_close_price(day, Env.DIFF_DAY_TOMORROW)
            stock_count = stock.get_stock_count()
            stock_amount = stock_price * stock_count
            account_amount += stock_amount
            account_foreign += stock.get_foreign()
        return account_amount, account_foreign

    def get_init_budget(self):
        return self.budget_init


class ForeignEnv(EnvBase):

    def __init__(self, _stock_num, _target_month, _budget=50000000):
        self.account = _AccountEnv(_budget)
        self.stock_num = _stock_num
        self.DataManager = DataManager.DataManager(self.stock_num)
        self.day_list = self.DataManager.get_daylist_in_month(_target_month)
        self.day_idx = 0
        self.account = ForeignAccount()

    def step(self, action_buys, action_sells):
        done = False
        day_target = self.day_list[self.day_idx]
        for buy_stock in action_buys:
            self.account.buy_stock(day_target, buy_stock)
        for sell_stock in action_sells:
            self.account.sell_stock(day_target, sell_stock)

        self.day_idx += 1
        if self.day_idx > len(self.day_list):
            done = True
            self.day_idx -= 1
        rewards, foreign = self.account.get_estimated_account(day_target)
        alpha = 0.9
        rewards = (rewards * (1-alpha)) * (alpha * foreign)
        if done:
            self.account.initialize()
        return rewards, self.day_list[self.day_idx], done

