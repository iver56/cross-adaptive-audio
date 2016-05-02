from __future__ import absolute_import
import settings
import analyze
import standardizer


class Project(object):
    def __init__(self, sounds):
        """
        Analyze a set of sounds, aggregate features and standardize series based on this
        """
        self.data = {}

        if settings.VERBOSE:
            print('Analyzing all sound files in project...')

        analyzer = analyze.Analyzer(project=None)
        analyzer.analyze_multiple(sounds, standardize=False)

        if settings.VERBOSE:
            print('Calculating standardization parameters...')
        s = standardizer.Standardizer(sounds)
        s.calculate_feature_statistics()
        self.data['feature_statistics'] = s.feature_statistics
        s.add_standardized_series()
