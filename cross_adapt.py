from __future__ import absolute_import
from __future__ import print_function
import argparse
import time
import template_handler
import csound_handler
import os
import settings
import sound_file


class CrossAdapter(object):
    NUM_PARAMETERS = 6

    def __init__(self):
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument(
            '-i',
            '--input',
            dest='input_files',
            nargs='+',
            type=str,
            help='The filename of the parameter sound and the filename of the input sound, respectively',
            required=True,
            default=[]
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

        if len(self.args.input_files) != 2:
            raise Exception('Two filenames must be specified')

        if self.args.print_execution_time:
            self.start_time = time.time()

        param_sound = sound_file.SoundFile(self.args.input_files[0])
        input_sound = sound_file.SoundFile(self.args.input_files[1])
        self.cross_adapt(input_sound, param_sound)

        if self.args.print_execution_time:
            print("execution time: %s seconds" % (time.time() - self.start_time))

    @staticmethod
    def cross_adapt(input_sound, param_sound):
        template = template_handler.TemplateHandler('templates/cross_adapt.csd.jinja2')
        template.compile(
            sound_filename=input_sound.filename,
            data_sound_filename=param_sound.filename,
            ksmps=settings.CSOUND_KSMPS,
            duration=input_sound.get_duration()
        )

        csd_path = os.path.join(settings.CSD_DIRECTORY, 'cross_adapt.csd')
        template.write_result(csd_path)
        csound = csound_handler.CsoundHandler(csd_path)
        output_filename = input_sound.filename + '.cross_adapted.{0}.{1}.wav'.format(
            input_sound.get_md5(),
            param_sound.get_md5()
        )
        csound.run(output_filename)
        output_sound_file = sound_file.SoundFile(output_filename, is_input=False)
        return output_sound_file

if __name__ == '__main__':
    CrossAdapter()
