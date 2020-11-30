from gensim.models.callbacks import CallbackAny2Vec
from datetime import datetime


class EpochLogger(CallbackAny2Vec):
    """
    Callback to log information about training
    """
    def __init__(self):
        self.epoch = 0

    def on_epoch_begin(self, model):
        print(f'{datetime.now()}: Model training epoch #{self.epoch} began')

    def on_epoch_end(self, model):
        print(f'{datetime.now()}: Model training epoch #{self.epoch} ended')
        self.epoch += 1
