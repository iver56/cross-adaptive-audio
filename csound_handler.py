import subprocess


class CsoundHandler(object):
    def __init__(self, csd_filename):
        self.csd_filename = csd_filename

    def run(self, output_filename):
        subprocess.call(
            [
                "csound",
                self.csd_filename,
                "-o " + output_filename
            ]
        )
