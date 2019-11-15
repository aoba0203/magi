import tensorflow as tf
import keras

# https://github.com/rlcode/reinforcement-learning-kr/blob/master/3-atari/1-breakout/breakout_a3c.py

class Model:
    ''' Super Class Model '''
    input_size = None

    # def __init__(self, input_size=64):
    #     self.input_size = input_size

    def get_model(self):
        model = keras.Sequential([
            keras.layers.Dense(self.input_size * 2, input_dim=self.input_size, activation='relu'),
            keras.layers.Dense(self.input_size * 4, activation='relu'),
            keras.layers.Dense(self.input_size * 8, activation='relu'),
            keras.layers.Dense(self.input_size * 4, activation='relu'),
            keras.layers.Dense(self.input_size * 2, activation='relu'),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(12, activation='tanh')
        ])
        model.compile(optimizer='rmsprop',)
        return model

