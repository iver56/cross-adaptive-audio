import settings
import os
import experiment
import csound_handler
import struct
import template_handler


class CsoundAnalyzer(object):
    AVAILABLE_FEATURES = {
        'csound_rms'
    }

    def __init__(self, features):
        if len(features) != 1 or 'csound_rms' not in features:
            raise Exception('Only csound_rms is implemented in csound_analyzer at the moment')
        self.features = features
        self.template = template_handler.TemplateHandler(
            os.path.join('csound_analyzers', 'csound_rms.csd.jinja2')
        )

    def analyze_multiple(self, sound_files):
        if len(sound_files) == 0:
            return

        for i in range(0, len(sound_files), settings.NUM_SIMULTANEOUS_PROCESSES):
            sound_files_batch = sound_files[i:i + settings.NUM_SIMULTANEOUS_PROCESSES]

            # run commands batch in parallel
            processes = [
                self.get_csound_handler(sound_file).run(
                    input_file_path=sound_file.file_path,
                    output_file_path=None,
                    async=True
                )
                for sound_file in sound_files_batch
                ]

            for j in range(len(processes)):
                processes[j].wait()

                self.parse_output(sound_files[i + j])
                self.clean_up(sound_files[i + j])

    def get_csound_handler(self, sound_file):
        output_analysis_file_path = self.get_output_analysis_file_path(sound_file)
        self.template.compile(
            ksmps=settings.HOP_SIZE,
            duration=sound_file.get_duration(),
            output_analysis_file_path=output_analysis_file_path
        )

        csd_path = self.get_csd_path(sound_file)
        self.template.write_result(csd_path)

        that_csound_handler = csound_handler.CsoundHandler(csd_path)
        return that_csound_handler

    @staticmethod
    def get_csd_path(sound_file):
        return os.path.join(
            settings.CSD_DIRECTORY,
            experiment.Experiment.folder_name,
            sound_file.filename + '.analyzer.csd'
        )

    @staticmethod
    def get_output_analysis_file_path(that_sound_file):
        return os.path.join(
            settings.TEMP_DIRECTORY,
            experiment.Experiment.folder_name,
            that_sound_file.filename + '.csound.bin'
        )

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
        return floats

    def parse_output(self, that_sound_file):
        for feature in self.features:
            that_sound_file.analysis['series'][feature] = []

        analysis_file_path = self.get_output_analysis_file_path(that_sound_file)

        floats = CsoundAnalyzer.read_32_bit_floats(analysis_file_path)

        for feature in self.features:
            that_sound_file.analysis['series'][feature] = floats

    def clean_up(self, that_sound_file):
        analysis_file_path = self.get_output_analysis_file_path(that_sound_file)
        os.remove(analysis_file_path)
        csd_file_path = self.get_csd_path(that_sound_file)
        os.remove(csd_file_path)
