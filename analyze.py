from __future__ import absolute_import
from __future__ import print_function
import argparse
import time
import template_handler
import csound_handler
import settings
import os
import sound_file
import subprocess
import logger
import standardizer
import project


class Analyzer(object):
    FEATURES = ['mfcc_time', 'mfcc_amp']
    for i in range(1, 13):
        FEATURES.append('mfcc_' + str(i))
    NUM_FEATURES = len(FEATURES)

    def __init__(self):
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument(
            '-i',
            '--input',
            dest='input_filename',
            type=str,
            help='The name of the input file',
            required=True
        )
        arg_parser.add_argument(
            '--standardize',
            nargs='?',
            dest='add_standardized_series',
            help='Add standardized series with respect to the current project as defined in settings.py',
            const=True,
            required=False,
            default=False
        )
        arg_parser.add_argument(
            '--print-execution-time',
            nargs='?',
            dest='print_execution_time',
            help='At the end of the run, print the execution time',
            const=True,
            required=False,
            default=False
        )
        self.args = arg_parser.parse_args()

        if self.args.print_execution_time:
            self.start_time = time.time()

        self.input_file_path = os.path.abspath(os.path.join(settings.INPUT_DIRECTORY, self.args.input_filename))
        self.sound_file_to_analyze = sound_file.SoundFile(self.args.input_filename)
        self.analyze(self.sound_file_to_analyze, self.args.add_standardized_series)

        if self.args.print_execution_time:
            print("execution time: %s seconds" % (time.time() - self.start_time))

    @staticmethod
    def analyze(sound_file_to_analyze, add_standardized_series=False):
        # Analyzer.analyze_rms(sound_file_to_analyze)
        Analyzer.analyze_mfcc(sound_file_to_analyze)

        if add_standardized_series:
            std = standardizer.Standardizer([sound_file_to_analyze])
            current_project = project.Project.get_current_project()
            std.set_feature_statistics(current_project)
            std.add_standardized_series()

    @staticmethod
    def analyze_rms(sound_file_to_analyze):
        # This method is unused
        template = template_handler.TemplateHandler('templates/rms_analyzer.csd.jinja2')
        template.compile(
            input_file_path=os.path.abspath(sound_file_to_analyze.file_path),
            ksmps=settings.CSOUND_KSMPS,
            duration=sound_file_to_analyze.get_duration(),
            feature_data_file_path=os.path.abspath(sound_file_to_analyze.get_feature_data_file_path())
        )
        csd_path = os.path.join(settings.CSD_DIRECTORY, 'rms_analyzer.csd')
        template.write_result(csd_path)
        csound = csound_handler.CsoundHandler(csd_path)
        csound.run()

    @staticmethod
    def analyze_mfcc(sound_file_to_analyze):
        command = [
            "aubiomfcc",  # assumes that aubio is installed

            '-i',
            os.path.abspath(sound_file_to_analyze.file_path),

            '--samplerate',
            str(settings.SAMPLE_RATE),

            '--bufsize',
            str(settings.AUBIO_BUFFER_SIZE),

            '--hopsize',
            str(settings.AUBIO_HOP_SIZE)
        ]
        stdout = subprocess.check_output(command).decode('utf-8')

        my_logger = logger.Logger(sound_file_to_analyze.get_feature_data_file_path(), Analyzer.FEATURES)

        for line in stdout.split('\n'):
            values = line.split()
            if not values:
                continue
            mfcc_time = float(values[0])
            my_logger.log_value('mfcc_time', mfcc_time)
            mfcc_amp = float(values[1])
            my_logger.log_value('mfcc_amp', mfcc_amp)
            for i in range(len(values) - 2):
                mfcc_band = float(values[i + 2])
                my_logger.log_value('mfcc_{}'.format(i + 1), mfcc_band)

        my_logger.write()

if __name__ == '__main__':
    Analyzer()
