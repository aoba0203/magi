from train.environment.EnvBase import EnvBase, _AccountEnv, _Stock
from train.environment import EnvBase as Env


class AgencyAccount(_AccountEnv):
    def buy_stock(self, day, stock_num):
        if stock_num not in self.dic_stock_on_hands:
            self.dic_stock_on_hands[stock_num] = _Stock(stock_num)
        stock = self.dic_stock_on_hands[stock_num]
        buy_price = stock.get_day_open_price(day, Env.DIFF_DAY_TOMORROW)
        buy_agency = stock.get_day_demand_agency(day)
        buy_count = int(self.budget_buying_per_stock / buy_price)
        buy_amount = buy_count * buy_price
        if buy_amount > self.budget_remain:
            print("Can't buy the stock: " + str(stock_num) + ', Amount: ' + str(buy_amount) + ", Remain: " + str(self.budget_remain))
        else:
            self.budget_remain -= buy_amount
            stock.buy(buy_count)
            self.dic_stock_on_hands[stock_num] = stock
            stock.buy_agency(buy_agency * buy_count)

    def sell_stock(self, day, stock_num):
        if stock_num not in self.dic_stock_on_hands.keys():
            return
        stock = self.dic_stock_on_hands[stock_num]
        sell_agency = stock.get_day_demand_agency(day)
        sell_count, empty = stock.sell()
        sell_amount = sell_agency * sell_count
        self.budget_remain += sell_amount
        self.dic_stock_on_hands[stock_num] = stock
        sell_agency = stock.get_day_demand_agency(day)
        stock.sell_agency(sell_agency * sell_count)
        if empty:
            del self.dic_stock_on_hands[stock_num]

    def get_estimated_account(self, day):
        account_amount = self.budget_remain
        account_agency = 0
        for key in self.dic_stock_on_hands.keys():
            stock = self.dic_stock_on_hands[key]
            stock_price = stock.get_day_close_price(day, Env.DIFF_DAY_TOMORROW)
            stock_count = stock.get_stock_count()
            stock_amount = stock_price * stock_count
            account_amount += stock_amount
            account_agency += stock.get_agency()
        return account_amount, account_agency

    def get_init_budget(self):
        return self.budget_init


class AgencyEnv(EnvBase):

    def set_account(self):
        self.account = AgencyAccount()

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
        rewards, agency = self.account.get_estimated_account(day_target)
        alpha = 0.9
        rewards = (rewards * (1-alpha)) * (alpha * agency)
        if done:
            self.account.initialize()
        return rewards, self.day_list[self.day_idx], done

