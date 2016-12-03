import settings
import os
import experiment
import csound_handler
import struct
import template_handler


class CsoundAnalyzer(object):
    AVAILABLE_FEATURES = {
        'csound_rms',
        'csound_spectral_centroid',
        'csound_pitch'
    }
    DIR = 'csound_analyzers'

    def __init__(self, features):
        assert 1 <= len(features) <= 4, 'Current implementation supports up to 4 Csound features'
        self.features = features
        self.features_order = list(features)
        self.feature_indexes = {
            self.features_order[i]: i
            for i in range(len(self.features_order))
            }
        template_file_path = os.path.join(self.DIR, 'csound_basic.csd.jinja2')
        with open(template_file_path, 'r') as template_file:
            template_string = template_file.read()
        self.template = template_handler.TemplateHandler(
            template_dir=self.DIR,
            template_string=template_string
        )

        self.template.compile(
            ksmps=settings.HOP_SIZE,
            frame_size=settings.FRAME_SIZE,
            features=self.features,
            features_order=self.features_order,
            num_features=len(self.features)
        )

        self.csd_path = os.path.join(
            settings.CSD_DIRECTORY,
            'csound_analyzer.csd'
        )
        self.template.write_result(self.csd_path)
        self.csound_handler = csound_handler.CsoundHandler(self.csd_path)

    def analyze_multiple(self, sound_files):
        if len(sound_files) == 0:
            return

        for i in range(0, len(sound_files), settings.NUM_SIMULTANEOUS_PROCESSES):
            sound_files_batch = sound_files[i:i + settings.NUM_SIMULTANEOUS_PROCESSES]

            # run commands batch in parallel
            processes = [
                self.csound_handler.run(
                    input_file_path=sound_file.file_path,
                    output_file_path=None,
                    async=True,
                    score_macros={
                        'DURATION': sound_file.get_duration()
                    },
                    orchestra_macros={
                        'OUTPUT_ANALYSIS_FILE_PATH': self.get_output_analysis_file_path(
                            sound_file,
                            use_forward_slashes=True
                        )
                    }
                )
                for sound_file in sound_files_batch
                ]

            for j in range(len(processes)):
                processes[j].wait()

                self.parse_output(sound_files[i + j])
                self.clean_up(sound_files[i + j])

    @staticmethod
    def get_output_analysis_file_path(that_sound_file, use_forward_slashes=False):
        # use_forward_slashes is used for Csound macros, even on Windows
        parts = []
        if use_forward_slashes:
            parts.append(settings.TEMP_DIRECTORY.replace('\\', '/'))
        else:
            parts.append(settings.TEMP_DIRECTORY)
        if len(experiment.Experiment.folder_name) > 2:
            parts.append(experiment.Experiment.folder_name)
        parts.append(that_sound_file.filename + '.csound.bin')

        if use_forward_slashes:
            return '/'.join(parts)
        else:
            return os.path.join(*parts)

    @staticmethod
    def unpack_numbers(numbers, num_series):
        return [
            numbers[i::num_series]
            for i in range(num_series)
        ]

    @staticmethod
    def read_32_bit_floats(file_path):
        num_bytes = os.path.getsize(file_path)
        with open(file_path, 'rb') as f:
            f = open(file_path, 'rb')
            n = num_bytes / 4
            floats = struct.unpack(
                '{0}f'.format(n),
                f.read(num_bytes)
            )
        return list(floats)

    def parse_output(self, that_sound_file):
        for feature in self.features:
            that_sound_file.analysis['series'][feature] = []

        analysis_file_path = self.get_output_analysis_file_path(that_sound_file)

        floats = CsoundAnalyzer.read_32_bit_floats(analysis_file_path)
        unpacked_series = self.unpack_numbers(floats, len(self.features))

        for feature in self.features:
            feature_index = self.feature_indexes[feature]
            that_sound_file.analysis['series'][feature] = unpacked_series[feature_index]

    def clean_up(self, that_sound_file):
        analysis_file_path = self.get_output_analysis_file_path(that_sound_file)
        os.remove(analysis_file_path)

    def final_clean_up(self):
        os.remove(self.csd_path)
