import settings
from subprocess import Popen, PIPE, STDOUT
import os
import json
import math
import experiment


class EssentiaAnalyzer(object):
    """
    Using this analyzer is not recommended, because by default it analyzes a lot of features, and
    one cannot easily disable features in the executable. This makes it computationally expensive.
    """
    AVAILABLE_FEATURES = {
        'barkbands_crest',
        'barkbands_flatness_db',
        'barkbands_kurtosis',
        'barkbands_skewness',
        'barkbands_spread',
        'dissonance',
        'erbbands_crest',
        'erbbands_flatness_db',
        'erbbands_kurtosis',
        'erbbands_skewness',
        'erbbands_spread',
        'melbands_crest',
        'melbands_flatness_db',
        'melbands_kurtosis',
        'melbands_skewness',
        'melbands_spread',
        'pitch_salience',
        'silence_rate_20dB',
        'silence_rate_30dB',
        'silence_rate_60dB',
        'spectral_centroid',
        'spectral_complexity',
        'spectral_decrease',
        'spectral_energy',
        'spectral_energyband_high',
        'spectral_energyband_low',
        'spectral_energyband_middle_high',
        'spectral_energyband_middle_low',
        'spectral_entropy',
        'spectral_flux',
        'spectral_kurtosis',
        'spectral_rms',
        'spectral_rolloff',
        'spectral_skewness',
        'spectral_spread',
        'spectral_strongpeak',
        'zerocrossingrate',

        # TODO: proper parsing. These are lists within lists
        # 'barkbands'
        # 'erbbands'
        # 'gfcc'
        # 'melbands'
        # 'mfcc'
        # 'spectral_contrast_coeffs',
        # 'spectral_contrast_valleys'

        # TODO: proper parsing and handling. These are single numbers.
        # 'average_loudness',
        # 'dynamic_complexity'
    }
    POST_PROCESSING = {
        'spectral_centroid': math.log
    }

    def __init__(self, features):
        self.features = features

    def analyze_multiple(self, sound_files):
        if len(sound_files) == 0:
            return

        commands = [self.get_command(sound) for sound in sound_files]

        for i in range(0, len(commands), settings.NUM_SIMULTANEOUS_PROCESSES):
            commands_batch = commands[i:i + settings.NUM_SIMULTANEOUS_PROCESSES]

            # run commands batch in parallel
            processes = [
                Popen(
                    command,
                    stdin=PIPE,
                    stdout=PIPE,
                    stderr=STDOUT
                )
                for command in commands_batch
                ]

            for j in range(len(processes)):
                processes[j].wait()
                stdout = processes[j].communicate()[0]
                if settings.VERBOSE:
                    print(stdout)
                if 'completely silent file' in stdout:
                    if settings.VERBOSE:
                        print('Discarding completely silent file')
                    sound_files[i + j].is_silent = True
                    continue

                self.parse_output(sound_files[i + j])
                self.post_process(sound_files[i + j])
                self.clean_up(sound_files[i + j])

    @staticmethod
    def get_output_analysis_file_path(that_sound_file):
        return os.path.join(
            settings.TEMP_DIRECTORY,
            experiment.Experiment.folder_name,
            that_sound_file.filename + '.json'
        )

    @staticmethod
    def get_command(that_sound_file):
        return [
            'streaming_extractor_music',
            os.path.abspath(that_sound_file.file_path),
            os.path.abspath(EssentiaAnalyzer.get_output_analysis_file_path(that_sound_file)),
            os.path.abspath(os.path.join('.', 'essentia_profile.yaml'))
        ]

    def parse_output(self, that_sound_file):
        for feature in self.features:
            that_sound_file.analysis['series'][feature] = []

        analysis_file_path = self.get_output_analysis_file_path(that_sound_file) + '_frames'

        with open(analysis_file_path, 'r') as analysis_file:
            data = json.load(analysis_file)

        for feature in self.features:
            that_sound_file.analysis['series'][feature] = data['lowlevel'][feature]

    def post_process(self, that_sound_file):
        for feature in self.features:
            if feature in self.POST_PROCESSING and self.POST_PROCESSING[feature]:
                that_sound_file.analysis['series'][feature] = map(
                    self.POST_PROCESSING[feature],
                    that_sound_file.analysis['series'][feature]
                )

    def clean_up(self, that_sound_file):
        analysis_file_path = self.get_output_analysis_file_path(that_sound_file)
        os.remove(analysis_file_path)
        os.remove(analysis_file_path + '_frames')
