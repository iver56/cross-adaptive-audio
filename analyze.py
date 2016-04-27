import settings
import standardizer
import project
import mfcc_analyzer
import essentia_analyzer
import copy


class Analyzer(object):
    FEATURES_LIST = copy.deepcopy(settings.NEURAL_INPUT_CHANNELS)
    for feature in settings.SIMILARITY_CHANNELS:
        if feature not in FEATURES_LIST:
            FEATURES_LIST.append(feature)

    FEATURES = {}
    for i in range(len(FEATURES_LIST)):
        label = FEATURES_LIST[i]
        FEATURES[label] = i
    NUM_FEATURES = len(FEATURES)

    AVAILABLE_ANALYZERS = [
        mfcc_analyzer.MfccAnalyzer,
        essentia_analyzer.EssentiaAnalyzer
    ]

    def __init__(self):
        self.project = project.Project.get_current_project()
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

        if len(features) > 0:
            raise Exception('Cannot analyze feature(s) {0}'.format(features))

    def add_standardized_series(self, sound_files):
        std = standardizer.Standardizer(sound_files)
        std.set_feature_statistics(self.project)
        std.add_standardized_series()

    def analyze_multiple(self, sound_files, standardize=True):
        for analyzer in self.analyzers:
            analyzer.analyze_multiple(sound_files)

        if standardize:
            self.add_standardized_series(sound_files)
