from train.agent import BaseModel
from keras.utils.np_utils import to_categorical
from keras import losses


class Casper(BaseModel.BaseModel):
    '''
        Price predict
    '''
    def get_casper_loss(self, y_true, y_pred):
        y_pred = to_categorical((y_pred * 2.5) + 2.4)
        y_true = to_categorical(y_true)
        return losses.categorical_crossentropy(y_true, y_pred)

    def train(self):
        self.model = self.build_model()
        self.model.compile(optimizer='rmsprop', loss=self.get_casper_loss, metrics=['accuracy'])
        self.model.fit(
            [self.train_x_raw, self.train_x_chart],
            self.train_y,
            epochs=self.epoch
        )
        self.model_evaluate_management(self.get_casper_loss, self.__class__.__name__)



# b = balthasar(64, 1, None, None)
# b.train()



