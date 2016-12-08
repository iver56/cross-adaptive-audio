from __future__ import absolute_import
from __future__ import print_function
import subprocess
import settings
import os


class CsoundHandler(object):
    CLOSE_FDS = os.name != 'nt'

    def __init__(self, csd_filename):
        self.csd_filename = csd_filename

        try:
            from subprocess import DEVNULL  # python 3
            self.devnull = DEVNULL
        except ImportError:
            self.devnull = open(os.devnull, 'wb')

    def run(self, input_file_path=None, output_file_path=None, async=False, score_macros=None, orchestra_macros=None):
        command = [
            "csound",
            self.csd_filename
        ]
        if output_file_path is not None:
            command.append('-o' + output_file_path)
        if input_file_path is not None:
            command.append('-i' + input_file_path)
        if score_macros is not None:
            for key, value in score_macros.items():
                command.append('--smacro:{0}={1}'.format(key, value))
        if orchestra_macros is not None:
            for key, value in orchestra_macros.items():
                command.append('--omacro:{0}={1}'.format(key, value))

        if settings.VERBOSE:
            p = subprocess.Popen(command, close_fds=self.CLOSE_FDS)
        else:
            p = subprocess.Popen(
                command,
                stdout=self.devnull,
                stderr=subprocess.STDOUT,
                close_fds=self.CLOSE_FDS
            )
        if not async:
            p.wait()
        return p
