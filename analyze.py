import argparse
import time
import template_handler
import csound_handler
import settings
import os
import sound_file
import subprocess
import re
import logger


class Analyze(object):
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
        self.sound_file_to_analyse = sound_file.SoundFile(self.args.input_filename)
        self.feature_data_file_path = self.sound_file_to_analyse.get_feature_data_file_path()
        self.analyze_rms()  # don't need this atm, since mfcc also analyzes amplitude
        self.analyze_mfcc()

        if self.args.print_execution_time:
            print "execution time: %s seconds" % (time.time() - self.start_time)

    def analyze_rms(self):
        template = template_handler.TemplateHandler('templates/rms_analyzer.csd.jinja2')
        template.compile(
            input_file_path=self.input_file_path,
            krate=settings.CSOUND_K_RATE,
            duration=self.sound_file_to_analyse.get_duration(),
            feature_data_file_path=self.feature_data_file_path
        )
        csd_path = os.path.join(settings.CSD_DIRECTORY, 'rms_analyzer.csd')
        template.write_result(csd_path)
        csound = csound_handler.CsoundHandler(csd_path)
        csound.run()

    def analyze_mfcc(self):
        command = [
            "aubiomfcc",  # assumes that aubio is installed

            '-i',
            self.input_file_path,

            '--samplerate',
            str(settings.SAMPLE_RATE),

            '--bufsize',
            str(settings.AUBIO_BUFFER_SIZE),

            '--hopsize',
            str(settings.AUBIO_HOP_SIZE)
        ]
        stdout = subprocess.check_output(command)

        features_to_add = ['mfcc_time', 'mfcc_amp']
        for i in range(1, 13):
            features_to_add.append('mfcc_' + str(i))

        my_logger = logger.Logger(self.feature_data_file_path, features_to_add)

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
    Analyze()
