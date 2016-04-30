from subprocess import PIPE, check_output
import os


class SonicAnnotatorAnalyzer(object):
    AVAILABLE_FEATURES = {
        'noisiness',
        'spectral_centroid',
        'spectral_inharmonicity',
        # TODO: add more features
    }

    def __init__(self, features):
        self.features = list(features)

    def analyze_multiple(self, sounds):
        if len(sounds) == 0:
            return

        for feature in self.features:
            command = self.get_command(sounds, feature)
            output = check_output(
                command,
                stderr=PIPE
            )
            self.parse_output(sounds, feature, output)

    def get_command(self, sounds, feature):
        command = [
            'sonic-annotator',
            '-t',
            os.path.join('sonic_annotator', feature + '.n3')
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

    def parse_output(self, sounds, feature, output):
        for sound in sounds:
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
            value = float(values[2])
            current_sound.analysis['series'][feature].append(value)
