from __future__ import absolute_import
from __future__ import print_function
import subprocess
import os
import settings


class CsoundHandler(object):
    def __init__(self, csd_filename):
        self.csd_filename = csd_filename

    def run(self, output_filename=None, async=False):
        command = [
            "csound",
            self.csd_filename
        ]
        if output_filename is not None:
            command.append('-o' + os.path.join(settings.OUTPUT_DIRECTORY, output_filename))

        if settings.VERBOSE:
            p = subprocess.Popen(command)
        else:
            devnull = open(os.devnull, 'w')
            p = subprocess.Popen(command, stdout=devnull)
        if not async:
            p.wait()
        return p
