from train.environment.EnvBase import EnvBase, _AccountEnv, _Stock
from train.environment import EnvBase as Env
from pprint import pprint


class PriceAccount(_AccountEnv):
    def buy_stock(self, day, stock_num):
        if stock_num not in self.dic_stock_on_hands:
            self.dic_stock_on_hands[stock_num] = _Stock(stock_num)
        stock = self.dic_stock_on_hands[stock_num]
        purchase_price = stock.get_day_open_price(day, Env.DIFF_DAY_TOMORROW)
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
        sell_price = stock.get_day_close_price(day, Env.DIFF_DAY_TOMORROW)
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
            stock_price = stock.get_day_close_price(day, Env.DIFF_DAY_TOMORROW)
            stock_count = stock.get_stock_count()
            stock_amount = stock_price * stock_count
            account_amount += stock_amount
        return account_amount

    def get_init_budget(self):
        return self.budget_init


class PriceEnv(EnvBase):

    def set_account(self):
        self.account = PriceAccount()

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
        rewards = self.account.get_estimated_account(day_target)
        if done:
            self.account.initialize()
        return rewards, self.day_list[self.day_idx], done

