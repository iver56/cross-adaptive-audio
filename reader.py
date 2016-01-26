import json
import os
import settings


class Reader(object):
    def __init__(self, data_filename):
        with open(os.path.join(settings.FEATURE_DATA_DIRECTORY, data_filename)) as data_file:
            self.data = json.load(data_file)
        self.current_k = {}
        for feature in self.data['series']:
            self.current_k[feature] = 0

    def get_next_value(self, feature):
        if self.current_k[feature] < len(self.data['series'][feature]):
            result = self.data['series'][feature][self.current_k[feature]]
            self.current_k[feature] += 1
            return result
        print 'out of range', self.current_k[feature]
        print 'feature', feature
        return 0.0
