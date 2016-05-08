from __future__ import absolute_import
from __future__ import print_function
import settings
import os


class Cleaner(object):
    @staticmethod
    def clean():
        paths = [
            settings.CSD_DIRECTORY,
            settings.INDIVIDUAL_DATA_DIRECTORY,
            settings.STATS_DATA_DIRECTORY,
            settings.OUTPUT_DIRECTORY,
            settings.TEMP_DIRECTORY
        ]
        extensions = ['.json', '.csd', '.wav', '.json_frames']

        for path in paths:
            for root, dirs, files in os.walk(path):
                for currentFile in files:
                    if any(currentFile.lower().endswith(ext) for ext in extensions):
                        if settings.VERBOSE:
                            print("Removing file: " + currentFile)
                        os.remove(os.path.join(root, currentFile))
        print('Done cleaning')


if __name__ == '__main__':
    Cleaner.clean()
