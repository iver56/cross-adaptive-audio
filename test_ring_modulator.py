import argparse
import time
import template_handler
import csound_handler


class Main(object):
    def __init__(self):
        arg_parser = argparse.ArgumentParser()
        """
        arg_parser.add_argument(
            '-i1',
            '--input1',
            dest='input1_filename',
            type=str,
            help='The name of the input1 file',
            required=True
        )
        arg_parser.add_argument(
            '-i2',
            '--input2',
            dest='input2_filename',
            type=str,
            help='The name of the input2 file',
            required=True
        )
        """
        arg_parser.add_argument(
            '--print-execution-time',
            nargs='?',
            dest='print_execution_time',
            help='At the end of the run, print the execution time',
            const=True,
            required=False,
            default=False
        )
        args = arg_parser.parse_args()

        if args.print_execution_time:
            self.start_time = time.time()

        self.run()

        if args.print_execution_time:
            print "execution time: %s seconds" % (time.time() - self.start_time)

    def run(self):
        template = template_handler.TemplateHandler('templates/ring_modulator.csd.jinja2')
        template.compile(filename='input/synth_remind_me.wav', iFreq=300)
        csd_path = 'csd/ring_modulator.csd'
        template.write_result(csd_path)
        csound = csound_handler.CsoundHandler(csd_path)
        csound.run('ring_modulator_test.wav')

if __name__ == '__main__':
    Main()
