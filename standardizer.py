import statistics
import pprint


class Standardizer(object):
    def __init__(self, sound_files):
        self.sound_files = sound_files
        self.feature_statistics = {}

    def calculate_feature_statistics(self):
        analyses = [sf.get_analysis() for sf in self.sound_files]
        print len(analyses), 'analyses'

        for key in analyses[0]['series']:
            self.feature_statistics[key] = {'min': None, 'max': None, 'mean': None, 'standard_deviation': None}

        for feature in self.feature_statistics:
            print 'analyzing feature', feature
            series = []
            for analysis in analyses:
                series += analysis['series'][feature]
                print 'local len', len(analysis['series'][feature])

            if len(series) == 0:
                continue

            self.feature_statistics[feature]['min'] = min(series)
            self.feature_statistics[feature]['max'] = max(series)
            self.feature_statistics[feature]['mean'] = statistics.mean(series)
            self.feature_statistics[feature]['standard_deviation'] = statistics.pstdev(series)

        pprint.pprint(self.feature_statistics)

    def standardize_value(self, feature, value):
        # TODO
        pass
