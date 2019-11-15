from model import model


class balthasar(model.Model):
    model = None

    def __init__(self, input_size=64):
        self.input_size = input_size

    def train(self):
        self.model = self.get_model()

