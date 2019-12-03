import numpy as np


class _DataSetManager:
    stock_df = None

    def __init__(self, _stock_df):
        self.stock_df = _stock_df

    def get_day_list_in_month(self, _target_yyyy_mm):
        df_month = self.get_datasets_by_month(_target_yyyy_mm)
        return np.sort(df_month.index[:-4].values)

    def get_datasets_by_month(self, _target_yyyy_mm):
        day_target_end = str(float(_target_yyyy_mm) + 0.01)
        df_sliced = self.stock_df.iloc[(_target_yyyy_mm < self.stock_df.index) & (self.stock_df.index < day_target_end)]
        date_end, date_start = df_sliced.index[0], df_sliced.index[-1]

        position_start = np.where(self.stock_df.index == date_end)[0][0]
        position_end = np.where(self.stock_df.index == date_start)[0][0] + 5

        df_month = self.stock_df.iloc[position_start: position_end]
        return df_month

    def get_sliced_dataset(self, _target_yyyy_mm):
        df_month = self.get_datasets_by_month(_target_yyyy_mm)
        df_data_list = []
        data_len = len(df_month) - 5
        for idx in list(range(data_len, -1, -1)):
            df_data_list.append(df_month.iloc[idx:(idx + 5)])
        return df_data_list
    