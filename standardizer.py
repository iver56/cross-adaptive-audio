from __future__ import absolute_import
from __future__ import print_function
import pprint
import settings
import math


class Standardizer(object):
    def __init__(self, sound_files):
        self.sound_files = sound_files
        self.feature_statistics = {}

    def calculate_feature_statistics(self):
        import statistics
        analyses = [sf.get_analysis() for sf in self.sound_files]

        for key in analyses[0]['series']:
            self.feature_statistics[key] = {'min': None, 'max': None, 'mean': None, 'standard_deviation': None}

        for feature in self.feature_statistics:
            if settings.VERBOSE:
                print('Analyzing {} feature statistics'.format(feature))
            series = []
            for analysis in analyses:
                series += analysis['series'][feature]

            if len(series) == 0:
                continue

            self.feature_statistics[feature]['min'] = min(series)
            self.feature_statistics[feature]['max'] = max(series)
            self.feature_statistics[feature]['mean'] = statistics.mean(series)
            self.feature_statistics[feature]['standard_deviation'] = statistics.pstdev(series)

        if settings.VERBOSE:
            pprint.pprint(self.feature_statistics)

    def set_feature_statistics(self, project):
        self.feature_statistics = project.data['feature_statistics']

    def add_standardized_series(self):
        print('Calculating and writing standardized series...')

        for sf in self.sound_files:
            analysis = sf.get_analysis()
            if 'series_standardized' not in analysis:
                analysis['series_standardized'] = {}
                for feature in self.feature_statistics:
                    analysis['series_standardized'][feature] = [
                        self.get_standardized_value(feature, value)
                        for value in analysis['series'][feature]
                        ]
                sf.write_analysis_data_cache()

    def get_standardized_value(self, feature, value):
        """
        :param feature:
        :param value:
        :return: A value that makes the series have zero mean and unit variance. Good for machine learning.
        """
        standardized_value = (value - self.feature_statistics[feature]['mean']) / \
                             self.feature_statistics[feature]['standard_deviation']
        standardized_value = max(min(standardized_value, 3), -3)  # clip extreme values
        return standardized_value

    @staticmethod
    def get_normalized_value(standardized_value):
        """
        :param standardized_value:
        :return: A value between 0 and 1. Good for visualization.
        """
        return 0.5 + math.tanh(standardized_value) / 2

    @staticmethod
    def get_mapped_value(normalized_value, min_value, max_value, skew_factor=1.0):
        """
        :param normalized_value: input value between 0 and 1
        :param min_value: minimum target value
        :param max_value: maximum target value
        :param skew_factor: a value between 0 and 1 gives exponential-like qualities. 1 => linear.
        :return: value between minimum and maximum with a specific skew
        """
        if skew_factor < 0:
            raise Exception('skew_factor must be positive')
        elif normalized_value < 0 or normalized_value > 1:
            raise Exception('normalized_value must be between 0 and 1 (inclusive)')
        elif min_value > max_value:
            raise Exception('min_value must not be greater than max_value')

        skewed_value = math.exp(math.log(normalized_value) / skew_factor)
        return min_value + (max_value - min_value) * skewed_value
