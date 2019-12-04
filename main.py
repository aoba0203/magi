import tensorflow as tf
from train.environment import EnvForeign, EnvPrice

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

from data import DataManager

DataManager.update_raw_data()

