import subprocess
import os


class CsoundHandler(object):
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

    def __init__(self, csd_filename):
        self.csd_filename = csd_filename

    def run(self, output_filename=None):
        command = [
            "csound",
            self.csd_filename
        ]
        if output_filename is not None:
            command.append('-o' + os.path.join(self.OUTPUT_DIR, output_filename))
        subprocess.call(command)
