import settings
from multiprocessing.dummy import Pool
from subprocess import Popen, PIPE, STDOUT
import os


class MfccAnalyzer(object):
    AVAILABLE_FEATURES = {
        'mfcc_0',
        'mfcc_1',
        'mfcc_2',
        'mfcc_3',
        'mfcc_4',
        'mfcc_5',
        'mfcc_6',
        'mfcc_7',
        'mfcc_8',
        'mfcc_9',
        'mfcc_10',
        'mfcc_11',
        'mfcc_12',
    }

    def __init__(self, features):
        self.features = features

    def analyze_multiple(self, sound_files):
        if len(sound_files) == 0:
            return

        commands = [self.get_command(sound) for sound in sound_files]

        # run commands in parallel
        processes = [
            Popen(
                command,
                stdout=PIPE,
                stderr=STDOUT
            )
            for command in commands
            ]

        # collect output in parallel
        def get_lines(process):
            return process.communicate()[0].splitlines()

        pool = Pool(len(processes))
        outputs = pool.map(get_lines, processes)
        pool.close()
        for i in range(len(sound_files)):
            self.parse_output(sound_files[i], outputs[i])

    @staticmethod
    def get_command(sound_file_to_analyze):
        return [
            "aubiomfcc",  # assumes that aubio is installed

            '-i',
            os.path.abspath(sound_file_to_analyze.file_path),

            '--samplerate',
            str(settings.SAMPLE_RATE),

            '--bufsize',
            str(settings.FRAME_SIZE),

            '--hopsize',
            str(settings.HOP_SIZE)
        ]

    def parse_output(self, sound_files, lines):
        for feature in self.features:
            sound_files.analysis['series'][feature] = []

        for line in lines:
            values = line.split()
            if not values:
                continue
            # mfcc_time = float(values[0])
            for i in range(len(values) - 1):
                feature_key = 'mfcc_{}'.format(i)
                if feature_key in self.features:
                    mfcc_coefficient = float(values[i + 1])
                    sound_files.analysis['series'][feature_key].append(mfcc_coefficient)

    def final_clean_up(self):
        pass
