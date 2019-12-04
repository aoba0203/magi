import tensorflow as tf
# from tensorflow.keras import layers
from tensorflow import keras
from data import DataManager
import os
from utils import utils

# https://github.com/rlcode/reinforcement-learning-kr/blob/master/3-atari/1-breakout/breakout_a3c.py
# https://github.com/yinchuandong/A3C-keras/blob/master/a3c.py
# https://github.com/seungeunrho/minimalRL/blob/master/a3c.py


class BaseModel:
    ''' Super Class Model '''
    dense_input = None
    cnn_input = None
    output_activation = None
    model_actor = None
    model_critic = None
    train_x_raw = None
    train_x_chart = None
    train_y = None
    eval_x = None
    eval_y = None
    epoch = None

    def __init__(self, _input_size, _output_size, output_activation='tanh'):
        self.input_size = _input_size
        self.output_size = _output_size
        self.output_activation = output_activation
        # self.train_x_raw = _train_x_raw
        # self.train_x_chart = _train_x_chart
        # self.train_y = _train_y
        # self.eval_x = _eval_x
        # self.eval_y = _eval_y
        self.epoch = 10

    def get_cnn_model(self):
        self.cnn_input = keras.layers.Input(shape=(299, 299, 5), name='cnn_input')
        model_cnn = keras.layers.Conv2D(64, kernel_size=(3, 3), activation='relu', strides=2, padding='same')(self.cnn_input)
        model_cnn = keras.layers.Conv2D(256, kernel_size=(3, 3), activation='relu', strides=2, padding='same')(model_cnn)
        # model_cnn = keras.layers.Conv2D(512, kernel_size=(3, 3), activation='relu', strides=2, padding='same')(model_cnn)
        model_cnn = keras.layers.Conv2D(256, kernel_size=(3, 3), activation='relu', strides=2, padding='same')(model_cnn)
        model_cnn = keras.layers.Conv2D(128, kernel_size=(3, 3), activation='relu', strides=2, padding='same')(model_cnn)
        model_cnn = keras.layers.AveragePooling2D((10, 10))(model_cnn)
        model_cnn = keras.layers.Flatten()(model_cnn)
        return model_cnn

    def get_dense_model(self):
        self.dense_input = keras.layers.Input(shape=(self.input_size,), name='dense_input')
        model_dense = keras.layers.Dense(128, activation='relu')(self.dense_input)
        model_dense = keras.layers.Dense(256, activation='relu')(model_dense)
        # model_dense = keras.layers.Dense(512, activation='relu')(model_dense)
        # model_dense = keras.layers.Dense(1024, activation='relu')(model_dense)
        # model_dense = keras.layers.Dense(512, activation='relu')(model_dense)
        model_dense = keras.layers.Dense(256, activation='relu')(model_dense)
        model_dense = keras.layers.Dense(128, activation='relu')(model_dense)
        return model_dense

    def get_dense_out_model(self, model_dense, model_cnn):
        model_share = keras.layers.concatenate([model_dense, model_cnn])
        model_share = keras.layers.Flatten()(model_share)
        model_share = keras.layers.Dense(512, activation='relu')(model_share)
        # model_out = keras.layers.Dense(1024, activation='relu')(model_out)
        # model_out = keras.layers.Dense(2048, activation='relu')(model_out)
        # model_out = keras.layers.Dense(1024, activation='relu')(model_out)

        model_actor = keras.layers.Dense(256, activation='relu')(model_share)
        model_actor = keras.layers.Dense(128, activation='relu')(model_actor)
        model_actor = keras.layers.Dense(self.output_size, activation=self.output_activation, name='model_out')(model_actor)

        model_critic = keras.layers.Dense(256, activation='relu')(model_share)
        model_critic = keras.layers.Dense(128, activation='relu')(model_critic)
        model_critic = keras.layers.Dense(1, activation=self.output_activation, name='model_out')(model_critic)
        return model_actor, model_critic

    def build_model(self):
        model_dense = self.get_dense_model()
        model_cnn = self.get_cnn_model()
        model_actor, model_critic = self.get_dense_out_model(model_dense, model_cnn)

        self.model_actor = keras.Model(inputs=[self.dense_input, self.cnn_input], outputs=[model_actor])
        self.model_critic = keras.Model(inputs=[self.dense_input, self.cnn_input], outputs=[model_critic])
        return self.model_actor, self.model_critic

    def get_global_model(self, _class_name):
        model_dense = self.get_dense_model()
        model_cnn = self.get_cnn_model()
        model_actor, model_critic = self.get_dense_out_model(model_dense, model_cnn)

        model_actor = keras.Model(inputs=[self.dense_input, self.cnn_input], outputs=[model_actor])
        model_critic = keras.Model(inputs=[self.dense_input, self.cnn_input], outputs=[model_critic])

        file_actor, file_critic = self.get_weight_file(_class_name)
        if file_actor is None:
            model_actor.load_weights(file_actor)
            model_critic.load_weights(file_critic)
        return model_actor, model_critic

    def get_model_weight_path(self, _class_name):
        paths = os.getcwd() + '/model_weight/' + _class_name + '/'
        if not os.path.exists(paths):
            os.makedirs(paths)
        return paths

    def get_weight_file(self, _class_name):
        best_loss_file = None
        best_loss = 100
        file_list = os.listdir(self.get_model_weight_path(_class_name))
        file_list.sort()
        # for file in file_list:
        #     loss = float(file.split('.')[0].split('_')[3])
        #     if best_loss > loss:
        #         best_loss = loss
        #         best_loss_file = file
        # return best_loss_file, best_loss
        actor = file_list[-2]
        critic = file_list[-1]
        return actor, critic

    def model_evaluate_and_save(self, _actor, _critic, _class_name):
        # self.model_actor.compile(optimizer='rmsprop', loss=_loss_func, metrics=['accuracy'])
        # loss, accuracy = self.model_actor.evaluate(self.eval_x, self.eval_y)
        #
        # _, best_loss = self.get_best_loss_file(_class_name)

        # if best_loss > loss:
        today = utils.get_today()
        time_now = utils.get_time()
        path = self.get_model_weight_path(_class_name)
        file_path = path + _class_name + '_' + today + '_' + time_now + '_'
        _actor.save_weights(file_path + 'actor.h5')
        _critic.save_weights(file_path + 'critic.h5')
