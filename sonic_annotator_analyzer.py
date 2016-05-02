from subprocess import PIPE, check_output
import os
import math


class SonicAnnotatorAnalyzer(object):
    AVAILABLE_FEATURES = {
        'spectral_centroid',
        'spectral_inharmonicity',
        'bark_0',
        'bark_1',
        'bark_2',
        'bark_3',
        'bark_4',
        'bark_5',
        'bark_6',
        'bark_7',
        'bark_8',
        'bark_9',
        'bark_10',
        'bark_11',
        'bark_12',
        'bark_13',
        'bark_14',
        'bark_15',
        'bark_16',
        'bark_17',
        'bark_18',
        'bark_19',
        'bark_20',
        'bark_21',
        'bark_22',
        'bark_23',
        'bark_24',
        'bark_25',
        'tristimulus_1',
        'tristimulus_2',
        'tristimulus_3'
    }

    # A mapping from individual vector entries to the name of the transform they belong two
    VECTOR_FEATURES = {
        'bark_0': 'bark_coefficients',
        'bark_1': 'bark_coefficients',
        'bark_2': 'bark_coefficients',
        'bark_3': 'bark_coefficients',
        'bark_4': 'bark_coefficients',
        'bark_5': 'bark_coefficients',
        'bark_6': 'bark_coefficients',
        'bark_7': 'bark_coefficients',
        'bark_8': 'bark_coefficients',
        'bark_9': 'bark_coefficients',
        'bark_10': 'bark_coefficients',
        'bark_11': 'bark_coefficients',
        'bark_12': 'bark_coefficients',
        'bark_13': 'bark_coefficients',
        'bark_14': 'bark_coefficients',
        'bark_15': 'bark_coefficients',
        'bark_16': 'bark_coefficients',
        'bark_17': 'bark_coefficients',
        'bark_18': 'bark_coefficients',
        'bark_19': 'bark_coefficients',
        'bark_20': 'bark_coefficients',
        'bark_21': 'bark_coefficients',
        'bark_22': 'bark_coefficients',
        'bark_23': 'bark_coefficients',
        'bark_24': 'bark_coefficients',
        'bark_25': 'bark_coefficients'
    }

    POST_PROCESSING = {
        # 'spectral_centroid': math.log
    }

    def __init__(self, features):
        self.features = list(features)

    def analyze_multiple(self, sounds):
        if len(sounds) == 0:
            return

        for feature in self.features:
            for sound in sounds:
                sound.analysis['series'][feature] = []

        for feature in self.features:
            if feature in self.VECTOR_FEATURES:
                if len(sounds[0].analysis['series'][feature]) == 0:
                    transform_name = self.VECTOR_FEATURES[feature]
                    command = self.get_command(sounds, transform_name)
                    output = check_output(
                        command,
                        stderr=PIPE
                    )
                    self.parse_vector_output(sounds, feature, output)
            else:
                command = self.get_command(sounds, feature)
                output = check_output(
                    command,
                    stderr=PIPE
                )
                self.parse_scalar_output(sounds, feature, output)

        for sound in sounds:
            self.post_process(sound)

    def get_command(self, sounds, transform_name):
        command = [
            'sonic-annotator',
            '-t',
            os.path.join('sonic_annotator', transform_name + '.n3')
        ]

        command += [
            # this program assumes forward slashes on both unix and windows
            os.path.abspath(sound.file_path).replace('\\', '/') for sound in sounds
            ]
        command += [
            '-w',
            'csv',
            '--csv-stdout',
        ]
        return command

    def parse_scalar_output(self, sounds, feature, output):
        lines = output.splitlines()
        current_sound_index = -1
        current_sound = None

        for line in lines:
            values = line.split(',')
            if values[0].startswith('"'):
                current_sound_index += 1
                current_sound = sounds[current_sound_index]
                file_path = values[0].replace('"', '')
                if current_sound.filename not in file_path:
                    raise Exception('Did not expect that file')
            # time = float(values[1])
            value = float(values[2])
            current_sound.analysis['series'][feature].append(value)

    def parse_vector_output(self, sounds, feature, output):
        lines = output.splitlines()
        current_sound_index = -1
        current_sound = None
        base_feature_name = feature.split('_')[0]

        for line in lines:
            values = line.split(',')
            if values[0].startswith('"'):
                current_sound_index += 1
                current_sound = sounds[current_sound_index]
                file_path = values[0].replace('"', '')
                if current_sound.filename not in file_path:
                    raise Exception('Did not expect that file')
            # time = float(values[1])

            for i in range(2, len(values)):
                feature_key = '{0}_{1}'.format(base_feature_name, i - 2)
                if feature_key in self.features:
                    value = float(values[i])
                    current_sound.analysis['series'][feature_key].append(value)

    def post_process(self, that_sound_file):
        for feature in self.features:
            if feature in self.POST_PROCESSING and self.POST_PROCESSING[feature]:
                that_sound_file.analysis['series'][feature] = map(
                    self.POST_PROCESSING[feature],
                    that_sound_file.analysis['series'][feature]
                )
