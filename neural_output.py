import os


class NeuralOutput(object):
    def __init__(self, data_file_path, channels):
        self.data_file_path = data_file_path
        self.channels = channels

    def delete(self):
        try:
            os.remove(self.data_file_path)
        except OSError:
            pass
