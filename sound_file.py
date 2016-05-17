from __future__ import absolute_import
import wave
import contextlib
import os
import settings
import analyze
import six
import experiment


class SoundFile(object):
    def __init__(self, filename, is_input=True, verify_file=False):
        self.is_input = is_input
        self.filename = filename
        if self.is_input:
            self.file_path = os.path.join(settings.INPUT_DIRECTORY, self.filename)
        else:
            self.file_path = os.path.join(
                settings.OUTPUT_DIRECTORY,
                experiment.Experiment.folder_name,
                self.filename
            )

        if verify_file:
            self.verify_file()
        
        self.duration = None
        self.analysis = {
            'ksmps': settings.HOP_SIZE,
            'series': {}
        }
        self.is_silent = False

    def verify_file(self):
        if not os.path.exists(self.file_path):
            raise Exception(
                'Could not find "{}". Make sure it exists and try again.'.format(self.file_path)
            )
        wav_properties = self.get_wav_properties()
        if wav_properties['num_frames'] < settings.FRAME_SIZE:
            raise Exception('The sound {} is too short'.format(self.file_path))
        if wav_properties['sample_rate'] != settings.SAMPLE_RATE:
            raise Exception(
                'Sample rate mismatch: The sample rate of {0} is {1} but should be {2}'.format(
                    self.file_path,
                    wav_properties['sample_rate'],
                    settings.SAMPLE_RATE
                )
            )
        if wav_properties['num_channels'] != 1:
            raise Exception(
                '{0} has {1} channels, but should have 1 (mono)'.format(
                    self.file_path,
                    wav_properties['num_channels']
                )
            )

    def get_wav_properties(self):
        with contextlib.closing(wave.open(self.file_path, 'r')) as f:
            num_frames = f.getnframes()
            sample_rate = f.getframerate()
            duration = num_frames / float(sample_rate)
            num_channels = f.getnchannels()

            return {
                'num_frames': num_frames,
                'sample_rate': sample_rate,
                'duration': duration,
                'num_channels': num_channels
            }

    def get_duration(self):
        if self.duration is None:
            self.duration = self.get_wav_properties()['duration']
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
        for feature in experiment.NEURAL_INPUT_CHANNELS:
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
