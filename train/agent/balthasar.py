from train.agent import BaseModel
from keras.utils.np_utils import to_categorical
from keras import losses


class Balthasar(BaseModel.BaseModel):
    global_model_actor = None
    global_model_critic = None
    '''
        foreign predict
    '''
    def get_balthasr_loss(self, y_true, y_pred):
        y_pred = to_categorical((y_pred * 2.5) + 2.4)
        y_true = to_categorical(y_true)
        return losses.categorical_crossentropy(y_true, y_pred)

    def train(self):


        self.model_actor, self.model_critic = self.build_model()

        self.model_actor._make_predict_function()
        self.model_critic._make_predict_function()


        self.model_evaluate_management(self.get_balthasr_loss, self.__class__.__name__)



# b = balthasar(64, 1, None, None)
# b.train()



