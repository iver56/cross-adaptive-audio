from subprocess import PIPE, check_output
import os


class SonicAnnotatorAnalyzer(object):
    AVAILABLE_FEATURES = {
        'noisiness',
        # 'spectral_centroid'
        # TODO: add more features
    }

    FEATURE_SETTINGS = {
        'noisiness': 'noisiness_settings.n3',
        # 'spectral_centroid': 'spectral_centroid_settings.n3'
    }

    def __init__(self, features):
        self.features = list(features)

    def analyze_multiple(self, sounds):
        if len(sounds) == 0:
            return

        command = self.get_command(sounds)

        output = check_output(
            command,
            stderr=PIPE
        )

        self.parse_output(sounds, output)

    def get_command(self, sounds):
        command = [
            'sonic-annotator'
        ]

        for feature in self.features:
            command += [
                '-t',
                os.path.join('sonic_annotator', self.FEATURE_SETTINGS[feature])
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

    def parse_output(self, sounds, output):
        for sound in sounds:
            for feature in self.features:
                sound.analysis['series'][feature] = []

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
            for i in range(len(self.features)):
                # TODO: This logic needs to be checked. See if it works with multiple features.
                value = float(values[i + 2])
                current_sound.analysis['series'][self.features[i]].append(value)
