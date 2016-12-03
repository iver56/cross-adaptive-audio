from __future__ import absolute_import
from __future__ import print_function
import subprocess
import settings


class CsoundHandler(object):
    def __init__(self, csd_filename):
        self.csd_filename = csd_filename

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
            p = subprocess.Popen(command)
        else:
            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if not async:
            p.wait()
        return p
