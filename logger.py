import json
import os
import settings
import gzip


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

    def write(self):
        output_file_path = os.path.join(settings.FEATURE_DATA_DIRECTORY, self.filename + ".json.gz")
        with gzip.GzipFile(output_file_path, 'wb') as outfile:
            json.dump(self.data, outfile)
