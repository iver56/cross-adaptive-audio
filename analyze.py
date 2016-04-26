import settings
import standardizer
import project
import mfcc_analyzer
import essentia_analyzer


class Analyzer(object):
    FEATURES_LIST = settings.ANALYZE_CHANNELS
    FEATURES = {}
    for i in range(len(FEATURES_LIST)):
        label = FEATURES_LIST[i]
        FEATURES[label] = i
    NUM_FEATURES = len(FEATURES)

    def __init__(self):
        self.project = project.Project.get_current_project()
        self.mfcc_analyzer = mfcc_analyzer.MfccAnalyzer({'mfcc_amp'})  # TODO: generalize
        # self.essentia_analyzer = essentia_analyzer.EssentiaAnalyzer(['spectral_centroid'])

    def add_standardized_series(self, sound_files):
        std = standardizer.Standardizer(sound_files)
        std.set_feature_statistics(self.project)
        std.add_standardized_series()

    def analyze_multiple(self, sound_files, standardize=True):
        self.mfcc_analyzer.analyze_multiple(sound_files)
        # self.essentia_analyzer.analyze_multiple(sound_files)

        if standardize:
            self.add_standardized_series(sound_files)
