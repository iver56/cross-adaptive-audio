from __future__ import absolute_import
from __future__ import print_function
import subprocess
import os
import settings


class CsoundHandler(object):
    def __init__(self, csd_filename):
        self.csd_filename = csd_filename

    def run(self, output_filename=None):
        command = [
            "csound",
            self.csd_filename
        ]
        if output_filename is not None:
            command.append('-o' + os.path.join(settings.OUTPUT_DIRECTORY, output_filename))

        stdout = subprocess.check_output(command)
        if settings.VERBOSE:
            print(stdout)
        return stdout
