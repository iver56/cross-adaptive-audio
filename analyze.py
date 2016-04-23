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
from multiprocessing.dummy import Pool
from subprocess import Popen, PIPE, STDOUT


class Analyzer(object):
    FEATURES_LIST = settings.ANALYZE_CHANNELS
    FEATURES = {}
    for i in range(len(FEATURES_LIST)):
        label = FEATURES_LIST[i]
        FEATURES[label] = i
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

        self.input_file_path = os.path.abspath(
            os.path.join(settings.INPUT_DIRECTORY, self.args.input_filename)
        )
        self.sound_file_to_analyze = sound_file.SoundFile(self.args.input_filename)
        self.analyze(self.sound_file_to_analyze, self.args.add_standardized_series)

        if self.args.print_execution_time:
            print("execution time: %s seconds" % (time.time() - self.start_time))

    @staticmethod
    def add_standardized_series(that_sound_file):
        std = standardizer.Standardizer([that_sound_file])
        current_project = project.Project.get_current_project()
        std.set_feature_statistics(current_project)
        std.add_standardized_series()

    @staticmethod
    def analyze(sound_file_to_analyze, add_standardized_series=False):
        # Analyzer.analyze_rms(sound_file_to_analyze)
        Analyzer.analyze_mfcc(sound_file_to_analyze)  # assuming that this is already done

        if add_standardized_series:
            Analyzer.add_standardized_series(sound_file_to_analyze)

    @staticmethod
    def analyze_rms(sound_file_to_analyze):
        # This method is unused
        template = template_handler.TemplateHandler('templates/rms_analyzer.csd.jinja2')
        template.compile(
            input_file_path=os.path.abspath(sound_file_to_analyze.file_path),
            ksmps=settings.CSOUND_KSMPS,
            duration=sound_file_to_analyze.get_duration(),
            feature_data_file_path=os.path.abspath(
                sound_file_to_analyze.get_feature_data_file_path())
        )
        csd_path = os.path.join(settings.CSD_DIRECTORY, 'rms_analyzer.csd')
        template.write_result(csd_path)
        csound = csound_handler.CsoundHandler(csd_path)
        csound.run()

    @staticmethod
    def get_analyze_mfcc_command(sound_file_to_analyze):
        return [
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

    @staticmethod
    def write_mfcc_analysis(sound_file_to_analyze, lines):
        # TODO: writing to file is inefficient.. let's handle it internally in python instead
        my_logger = logger.Logger(sound_file_to_analyze.get_feature_data_file_path(),
                                  Analyzer.FEATURES)

        for line in lines:
            values = line.split()
            if not values:
                continue
            # mfcc_time = float(values[0])
            # my_logger.log_value('mfcc_time', mfcc_time)
            mfcc_amp = float(values[1])
            if 'mfcc_amp' in Analyzer.FEATURES:
                my_logger.log_value('mfcc_amp', mfcc_amp)
            for i in range(len(values) - 2):
                mfcc_band = float(values[i + 2])
                feature_key = 'mfcc_{}'.format(i + 1)
                if feature_key in Analyzer.FEATURES:
                    my_logger.log_value(feature_key, mfcc_band)

        my_logger.write()

    @staticmethod
    def analyze_mfcc(sound_file_to_analyze):
        # TODO: this method may be removed in the future
        command = Analyzer.get_analyze_mfcc_command(sound_file_to_analyze)
        stdout = subprocess.check_output(command).decode('utf-8')
        lines = stdout.split('\n')
        Analyzer.write_mfcc_analysis(sound_file_to_analyze, lines)

    @staticmethod
    def analyze_mfcc_parallel(sound_files_to_analyze):
        commands = [Analyzer.get_analyze_mfcc_command(sound) for sound in sound_files_to_analyze]

        # run commands in parallel
        processes = [
            Popen(
                command,
                stdin=PIPE,
                stdout=PIPE,
                stderr=STDOUT
            )
            for command in commands
            ]

        # collect output in parallel
        def get_lines(process):
            return process.communicate()[0].splitlines()

        outputs = Pool(len(processes)).map(get_lines, processes)
        for i in range(len(sound_files_to_analyze)):
            Analyzer.write_mfcc_analysis(sound_files_to_analyze[i], outputs[i])


if __name__ == '__main__':
    Analyzer()
