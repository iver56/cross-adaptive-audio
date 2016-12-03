import settings
import standardizer
import sonic_annotator_analyzer
import mfcc_analyzer
import essentia_analyzer
import csound_analyzer
import copy
import experiment


class Analyzer(object):
    FEATURES_LIST = None
    FEATURES = None
    NUM_FEATURES = None

    AVAILABLE_ANALYZERS = [
        sonic_annotator_analyzer.SonicAnnotatorAnalyzer,
        mfcc_analyzer.MfccAnalyzer,
        essentia_analyzer.EssentiaAnalyzer,
        csound_analyzer.CsoundAnalyzer
    ]

    @staticmethod
    def init_features_list():
        Analyzer.FEATURES_LIST = copy.deepcopy(experiment.Experiment.NEURAL_INPUT_CHANNELS)
        for feature in experiment.Experiment.SIMILARITY_CHANNELS:
            if feature not in Analyzer.FEATURES_LIST:
                Analyzer.FEATURES_LIST.append(feature)

        Analyzer.FEATURES = {}
        for i in range(len(Analyzer.FEATURES_LIST)):
            label = Analyzer.FEATURES_LIST[i]
            Analyzer.FEATURES[label] = i
        Analyzer.NUM_FEATURES = len(Analyzer.FEATURES)

    def __init__(self, project):
        self.project = project
        self.analyzers = []

        features = set(self.FEATURES_LIST)

        for analyzer_class in self.AVAILABLE_ANALYZERS:
            relevant_features = analyzer_class.AVAILABLE_FEATURES.intersection(features)
            if len(relevant_features) > 0:
                if settings.VERBOSE:
                    print('Initializing', analyzer_class)
                analyzer_instance = analyzer_class(relevant_features)
                self.analyzers.append(analyzer_instance)
                features -= relevant_features

        self.derivative_features = set()

        for feature in features:
            if feature.endswith('__derivative'):
                self.derivative_features.add(feature)
        features -= self.derivative_features

        if len(features) > 0:
            raise Exception('Cannot analyze feature(s) {0}'.format(features))

    def add_derivative_series(self, sound_files):
        for derivative_feature in self.derivative_features:
            feature = derivative_feature.replace('__derivative', '')
            for sound in sound_files:
                sound.analysis['series'][
                    derivative_feature
                ] = standardizer.Standardizer.get_derivative_series(
                    sound.analysis['series'][feature]
                )

    def add_standardized_series(self, sound_files):
        std = standardizer.Standardizer(sound_files)
        std.set_feature_statistics(self.project)
        std.add_standardized_series()

    def analyze_multiple(self, sound_files, standardize=True):
        for analyzer in self.analyzers:
            analyzer.analyze_multiple(sound_files)

        self.ensure_equal_lengths(sound_files, series_key='series')

        self.add_derivative_series(sound_files)

        if standardize:
            self.add_standardized_series([sf for sf in sound_files if not sf.is_silent])

    def ensure_equal_lengths(self, sounds, series_key='series'):
        # Check if series length is equal for all series, and if not, try to fix it with padding
        for sound in sounds:
            series_lengths = [
                len(sound.analysis[series_key][feature])
                for feature in sound.analysis[series_key]
                ]

            min_series_length = min(series_lengths)
            max_series_length = max(series_lengths)

            if min_series_length != max_series_length:
                if max_series_length - min_series_length <= 16:
                    if settings.VERBOSE:
                        print('Slight series length mismatch. Will apply padding to fix this.')
                    self.right_pad_series(sound, max_series_length)
                else:
                    for feature in sound.analysis[series_key]:
                        print(
                            'len({0}) = {1}'.format(
                                feature,
                                len(sound.analysis[series_key][feature])
                            )
                        )
                    raise Exception('Series length mismatch ({0} vs. {1})'.format(
                        min_series_length,
                        max_series_length
                    ))

    def right_pad_series(self, sound, max_series_length):
        for feature in sound.analysis['series']:
            num_missing = max_series_length - len(sound.analysis['series'][feature])
            if num_missing > 0:
                for _ in range(num_missing):
                    sound.analysis['series'][feature].append(
                        sound.analysis['series'][feature][-1]
                    )

    def final_clean_up(self):
        for analyzer in self.analyzers:
            analyzer.final_clean_up()
