from __future__ import absolute_import
import json
import settings
import os


class Logger(object):
    def __init__(self, feature_data_file_path, features_to_add=None, suppress_initialization=False):
        self.feature_data_file_path = feature_data_file_path
        self.data = None
        self.buffer = None  # holds a value temporarily before it is stored in an array
        if not suppress_initialization:
            self.read_existing()
            if self.data is None:
                self.data = {
                    'ksmps': settings.CSOUND_KSMPS,
                    'series': {
                        'time': []
                    }
                }
            if features_to_add is not None:
                for feature in features_to_add:
                    self.data['series'][feature] = []

    def read_existing(self):
        if os.path.isfile(self.feature_data_file_path):
            with settings.FILE_HANDLER(self.feature_data_file_path) as data_file:
                self.data = json.load(data_file)

    def log_buffer(self, feature):
        self.data['series'][feature].append(self.buffer)
        self.buffer = None

    def log_value(self, feature, value):
        self.data['series'][feature].append(value)

    def write(self):
        with settings.FILE_HANDLER(self.feature_data_file_path, 'w') as outfile:
            json.dump(self.data, outfile)
