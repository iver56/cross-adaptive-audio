from __future__ import absolute_import
from __future__ import print_function
import settings
import os
import shutil


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

        for path in paths:
            for root, dirs, files in os.walk(path):
                if dirs:
                    for experiment_dir in dirs:
                        folder_to_delete = os.path.join(path, experiment_dir)
                        if settings.VERBOSE:
                            print('Deleting folder {}'.format(folder_to_delete))
                        shutil.rmtree(folder_to_delete)
        print('Done cleaning')


if __name__ == '__main__':
    Cleaner.clean()
