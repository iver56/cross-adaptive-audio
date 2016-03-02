import os
import settings


class NeuralOutput(object):
    def __init__(self, data_file_path, channels):
        self.data_file_path = data_file_path
        self.channels = channels
