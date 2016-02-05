import json
import os
import settings
import sound_file


class Reader(object):
    def __init__(self, data_sound_filename):
        sf = sound_file.SoundFile(data_sound_filename)
        with settings.FILE_HANDLER(sf.get_feature_data_file_path(), 'rb') as data_file:
            self.data = json.load(data_file)
        self.current_k = {}
        for feature in self.data['series_standardized']:
            self.current_k[feature] = 0

    def get_next_value(self, feature):
        result = self.data['series_standardized'][feature][self.current_k[feature]]
        if self.current_k[feature] + 1 < len(self.data['series_standardized'][feature]):
            self.current_k[feature] += 1
        return result
