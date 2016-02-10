from __future__ import absolute_import
import json
import settings


class Reader(object):
    def __init__(self, data_file_path):
        with settings.FILE_HANDLER(data_file_path, 'rb') as data_file:
            self.data = json.load(data_file)
        self.current_k = 0

    def get_current_channel_value(self, channel_index):
        return self.data[channel_index][self.current_k]

    def increment_k(self):
        self.current_k += 1
