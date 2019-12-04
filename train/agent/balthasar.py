from train.agent import BaseModel
from keras.utils.np_utils import to_categorical
from keras import losses
from train.environment import EnvForeign
from data import DayUtils, DataManager
import threading

global_actor = None
global_critic = None


class Balthasar(BaseModel.BaseModel):
    global global_actor
    global global_critic
    '''
        foreign predict
    '''
    def __init__(self, _stock_num, _input_size, _output_size, output_activation='tanh'):
        global global_actor, global_critic
        self.stock_num = _stock_num
        self.input_size = _input_size
        self.output_size = _output_size
        self.output_activation = output_activation
        self.epoch = 10
        global_actor, global_critic = self.get_global_model(self.__class__.__name__)
        self.month_list = DayUtils.get_month_list(_stock_num)

    def train(self):
        self.model_actor._make_predict_function()
        self.model_critic._make_predict_function()



class Agent(threading.Thread):
    def __init__(self, _stock_num, _target_month, _global_actor, _global_critic):
        self.global_actor = _global_actor
        self.global_critic = _global_critic
        self.local_actor, self.local_critic = BaseModel.BaseModel(64, 1).build_model()
        self.local_actor._make_predict_function()
        self.local_critic._make_predict_function()
        self.local_actor.set_weights(self.global_actor.get_weights())
        self.local_critic.set_weights(self.global_critic.get_weights())
        self.EnvForeign = EnvForeign.ForeignEnv(_stock_num, _target_month)
        dataManager = DataManager.DataManager(_stock_num)
        self.day_list = dataManager.get_daylist_in_month(_target_month)
        self.dataset_list = dataManager.get_dataset_in_month(_target_month)

    def run(self):
        env = self.EnvForeign

        for idx, day in enumerate(self.day_list):
            done = False
            dense_data = self.dataset_list[idx]

    def get_action(self, dense_data, cnn_data):
        self.local_actor.predict({'dense_input': dense_data, 'cnn_input':cnn_data})

    def get_cnn_dataset(self, day):
        DayUt






# b = balthasar(64, 1, None, None)
# b.train()



