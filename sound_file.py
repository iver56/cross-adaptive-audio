from __future__ import absolute_import
import wave
import contextlib
import os
import settings
import analyze
import six


class SoundFile(object):
    def __init__(self, filename, is_input=True):
        self.is_input = is_input
        self.filename = filename
        if self.is_input:
            self.file_path = os.path.join(settings.INPUT_DIRECTORY, self.filename)
        else:
            self.file_path = os.path.join(settings.OUTPUT_DIRECTORY, self.filename)
        
        self.duration = None
        self.analysis = {
            'ksmps': settings.HOP_SIZE,
            'series': {}
        }

    def compute_duration(self):
        with contextlib.closing(wave.open(self.file_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            return duration

    def get_duration(self):
        if self.duration is None:
            self.duration = self.compute_duration()
        return self.duration

    def get_num_frames(self):
        arbitrary_series = six.next(six.itervalues(self.analysis['series']))
        return len(arbitrary_series)

    def get_standardized_neural_input_vector(self, k):
        """
        Get a neural input vector for a given frame k.
        Assumes that self.analysis['series_standardized'] is defined and k is within bounds.
        May raise an exception otherwise
        :param k:
        :return: list
        """
        feature_vector = []
        for feature in settings.NEURAL_INPUT_CHANNELS:
            feature_vector.append(self.analysis['series_standardized'][feature][k])
        return feature_vector

    def get_serialized_representation(self):
        self.analysis['order'] = analyze.Analyzer.FEATURES_LIST
        return {
            'feature_data': self.analysis,
            'filename': self.filename,
            'is_input': self.is_input
        }

    def delete(self):
        try:
            os.remove(self.file_path)
        except OSError:
            pass
