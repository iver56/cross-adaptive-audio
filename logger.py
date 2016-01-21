import json
import os


class Logger(object):
    def __init__(self, krate, filename, features):
        self.filename = filename
        self.data = {
            'krate': krate,
            'filename': filename,
            'series': {}
        }
        for feature in features:
            self.data['series'][feature] = []
        self.buffer = None  # holds a value temporarily before it is stored in an array
        self.k = 0

    def log(self, feature):
        self.data['series'][feature].append(self.buffer)
        self.buffer = None

        # TODO: remove this
        if len(self.data['series'][feature]) % 1000 == 999:
            self.write()

    def write(self):
        with open(os.path.join('feature_data', self.filename + ".json"), 'wb') as outfile:
            json.dump(self.data, outfile)
