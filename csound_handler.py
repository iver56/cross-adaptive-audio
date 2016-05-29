from __future__ import absolute_import
from __future__ import print_function
import subprocess
import os
import settings
import experiment


class CsoundHandler(object):
    def __init__(self, csd_filename):
        self.csd_filename = csd_filename

    def run(self, input_filename=None, output_filename=None, async=False):
        command = [
            "csound",
            self.csd_filename
        ]
        if output_filename is not None:
            output_file_path = os.path.join(
                settings.OUTPUT_DIRECTORY,
                experiment.Experiment.folder_name,
                output_filename
            )
            command.append('-o' + output_file_path)
        input_file_path = os.path.join(
            settings.INPUT_DIRECTORY,
            input_filename
        )
        command.append('-i' + input_file_path)

        if settings.VERBOSE:
            p = subprocess.Popen(command)
        else:
            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if not async:
            p.wait()
        return p
