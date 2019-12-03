import tensorflow as tf
from train.env import EnvForeign, EnvPrice

# print(tf.__version__)
# foreign = EnvForeign.ForeignAccount()
# print('load Foreign')
# price = EnvPrice.PriceAccount()
# print('load price')
#
# foreign.buy_stock('2019.11.04', '066570')
# print('buy stock')
# foreign.buy_stock('2019.11.05', '066570')
# print('buy stock')
# price.buy_stock('2019.11.06', '066570')
# price.buy_stock('2019.11.07', '066570')
# price.buy_stock('2019.11.08', '066570')
# print('buy stock')
#
# print(foreign.print_account_state('2019.11.08'))
# print(price.print_account_state('2019.11.08'))

class A:
    title = 'title_a'

    def print_a(self):
        print(__class__.__name__)
        print(self.title)


class B(A):
    title = 'title_b'

    def print_b(self):
        self.print_a()
        print(__class__.__name__)

class C(A):
    title = 'title_c'
    def print_c(self):
        self.print_a()
        print(__class__.__name__)

B().print_b()
C().print_c()
B().print_b()
