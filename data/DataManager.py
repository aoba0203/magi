from data import DataGather
from data import DatasetMaker
from data import DayUtils, DataUtils


class DataManager:
    DataGather = None
    DatasetManager = None
    DayUtils = None

    stock_num = None
    stock_df = None

    def __init__(self, _stock_num):
        self.DataGather = DataGather._DataGather(_stock_num)
        print('DataGather.get_stock_data_frame')
        self.stock_df = self.DataGather.get_stock_data_frame()
        print('DatasetMaker')
        self.DatasetManager = DatasetMaker._DataSetManager(self.stock_df)
        self.DayUtils = DayUtils.DayUtils(self.stock_df)

        self.stock_num = _stock_num

    def get_dataframe(self):
        return self.stock_df

    def get_daylist_in_month(self, _target_month):
        return self.DatasetManager.get_day_list_in_month(_target_month)

    def get_raw_path(self):
        return DataUtils.get_raw_data_path()

    def get_chart_path(self):
        return DataUtils.get_chart_data_path()





# def get_sliced_dataset(df_month):
#     df_data_list = []
#     data_len = len(df_month) - 5
#     for idx in list(range(data_len, -1, -1)):
#         df_data_list.append(df_month.iloc[idx:(idx +5)])
#     return df_data_list


if __name__ == '__main__':
    # df = DataManager('066570').get_dataframe()
    # print(df)
    print()