from __future__ import absolute_import
from __future__ import print_function
import settings
import os
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
        pass

    @staticmethod
    def add_standardized_series(that_sound_file):
        std = standardizer.Standardizer([that_sound_file])
        current_project = project.Project.get_current_project()
        std.set_feature_statistics(current_project)
        std.add_standardized_series()

    @staticmethod
    def analyze_multiple(sound_files_to_analyze, standardize=False):
        Analyzer.analyze_mfcc_parallel(sound_files_to_analyze)

        if standardize:
            # TODO: have a call that can do this for all at once instead
            for s in sound_files_to_analyze:
                Analyzer.add_standardized_series(s)

    @staticmethod
    def analyze_rms(sound_file_to_analyze):
        # This method is unused and may be removed in the future
        """
        template = template_handler.TemplateHandler('templates/rms_analyzer.csd.jinja2')
        template.compile(
            input_file_path=os.path.abspath(sound_file_to_analyze.file_path),
            ksmps=settings.CSOUND_KSMPS,
            duration=sound_file_to_analyze.get_duration(),
            feature_data_file_path=os.path.abspath(
                sound_file_to_analyze.get_feature_data_file_path()  # TODO: use other path
            )
        )
        csd_path = os.path.join(settings.CSD_DIRECTORY, 'rms_analyzer.csd')
        template.write_result(csd_path)
        csound = csound_handler.CsoundHandler(csd_path)
        csound.run()
        """
        pass

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
    def parse_mfcc_analysis(sound_file_to_analyze, lines):
        for feature in Analyzer.FEATURES:
            sound_file_to_analyze.analysis['series'][feature] = []

        for line in lines:
            values = line.split()
            if not values:
                continue
            # mfcc_time = float(values[0])
            if 'mfcc_amp' in Analyzer.FEATURES:
                mfcc_amp = float(values[1])
                sound_file_to_analyze.analysis['series']['mfcc_amp'].append(mfcc_amp)
            for i in range(len(values) - 2):
                feature_key = 'mfcc_{}'.format(i + 1)
                if feature_key in Analyzer.FEATURES:
                    mfcc_band = float(values[i + 2])
                    sound_file_to_analyze.analysis['series'][feature_key].append(mfcc_band)

    @staticmethod
    def analyze_mfcc_parallel(sound_files_to_analyze):
        if len(sound_files_to_analyze) == 0:
            return

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
            Analyzer.parse_mfcc_analysis(sound_files_to_analyze[i], outputs[i])
