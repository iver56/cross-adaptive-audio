import json
import os
import settings


class Reader(object):
    def __init__(self, data_sound_filename):
        data_file_path = os.path.join(settings.FEATURE_DATA_DIRECTORY, data_sound_filename + settings.DATA_FILE_EXTENSION)
        with settings.FILE_HANDLER(data_file_path, 'rb') as data_file:
            self.data = json.load(data_file)
        self.current_k = {}
        for feature in self.data['series']:
            self.current_k[feature] = 0

    def get_next_value(self, feature):
        result = self.data['series'][feature][self.current_k[feature]]
        if self.current_k[feature] + 1 < len(self.data['series'][feature]):
            self.current_k[feature] += 1
        return result
