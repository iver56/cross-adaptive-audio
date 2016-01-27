import hashlib
import wave
import contextlib
import json
import os
import settings


class SoundFile(object):
    def __init__(self, filename, is_input=True):
        self.is_input = is_input
        self.filename = filename
        if self.is_input:
            self.file_path = os.path.join(settings.INPUT_DIRECTORY, self.filename)
        else:
            self.file_path = os.path.join(settings.OUTPUT_DIRECTORY, self.filename)
        
        self.md5 = None
        self.get_md5()
        self.duration = None
        self.fetch_cache()

    def get_md5(self):
        if self.md5 is None:
            my_hash = hashlib.md5()
            with open(self.file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    my_hash.update(chunk)
            self.md5 = my_hash.hexdigest()
        return self.md5

    def compute_duration(self):
        with contextlib.closing(wave.open(self.file_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            return duration

    def get_duration(self):
        if self.duration is None:
            self.duration = self.compute_duration()
            self.write_cache()
        return self.duration

    def get_cache_file_path(self):
        return os.path.join('meta_data_cache', self.filename + '.' + self.get_md5() + '.json')

    def fetch_cache(self):
        cache_file_path = self.get_cache_file_path()
        if os.path.isfile(cache_file_path):
            with open(cache_file_path) as data_file:
                data = json.load(data_file)
            if 'duration' in data and data['duration']:
                self.duration = data['duration']

    def write_cache(self):
        with open(self.get_cache_file_path(), 'wb') as outfile:
            data = {}
            if self.duration:
                data['duration'] = self.duration
            json.dump(data, outfile)
