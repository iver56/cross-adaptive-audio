import argparse
import time
import template_handler
import csound_handler
import os
import settings
import sound_file


class CrossAdapt(object):
    def __init__(self):
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument(
            '-s',
            '--sound',
            dest='sound_filename',
            type=str,
            help='The name of the sound file to be processed',
            required=True
        )
        arg_parser.add_argument(
            '-d',
            '--data',
            dest='data_filename',
            type=str,
            help='The name of the data (json) file to be used as basis for input to the effect',
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

        self.run()

        if self.args.print_execution_time:
            print "execution time: %s seconds" % (time.time() - self.start_time)

    def run(self):
        template = template_handler.TemplateHandler('templates/cross_adapt.csd.jinja2')
        sound_file_to_analyse = sound_file.SoundFile(self.args.sound_filename)
        duration = sound_file_to_analyse.get_duration()
        template.compile(
            sound_filename=self.args.sound_filename,
            data_filename=self.args.data_filename,
            krate=settings.DEFAULT_K_RATE,
            duration=duration
        )

        csd_path = os.path.join(settings.CSD_DIRECTORY, 'cross_adapt.csd')
        template.write_result(csd_path)
        csound = csound_handler.CsoundHandler(csd_path)
        output_filename = self.args.sound_filename + '.processed.wav'
        csound.run(output_filename)

if __name__ == '__main__':
    CrossAdapt()
