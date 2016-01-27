import json
import os
import settings


class Logger(object):
    def __init__(self, krate, output_file_path, features):
        self.output_file_path = output_file_path
        self.data = {
            'krate': krate,
            'series': {}
        }
        for feature in features:
            self.data['series'][feature] = []
        self.buffer = None  # holds a value temporarily before it is stored in an array
        self.k = 0

    def log(self, feature):
        self.data['series'][feature].append(self.buffer)
        self.buffer = None

    def write(self):
        with settings.FILE_HANDLER(self.output_file_path, 'wb') as outfile:
            json.dump(self.data, outfile)
