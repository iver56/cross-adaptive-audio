from __future__ import absolute_import
from __future__ import print_function
import settings
import os
import argparse


class Cleaner(object):
    @staticmethod
    def clean(keep_project_data=True, keep_input_feature_data=True):
        """
        Remove feature data and meta data cache
        :param keep_project_data:
        :param keep_input_feature_data:
        :return:
        """
        paths = [
            settings.OUTPUT_FEATURE_DATA_DIRECTORY,
            settings.CSD_DIRECTORY,
            settings.NEURAL_OUTPUT_DIRECTORY
        ]
        if not keep_input_feature_data:
            paths.append(settings.INPUT_FEATURE_DATA_DIRECTORY)
            paths.append(settings.META_DATA_CACHE_DIRECTORY)
        if not keep_project_data:
            paths.append(settings.PROJECT_DATA_DIRECTORY)
        for path in paths:
            for root, dirs, files in os.walk(path):
                for currentFile in files:
                    extensions = ('.json', '.csd')
                    if any(currentFile.lower().endswith(ext) for ext in extensions):
                        print("Removing file: " + currentFile)
                        os.remove(os.path.join(root, currentFile))

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--keep-project-data',
        dest='keep_project_data',
        nargs='?',
        const=True,
        required=False,
        default=False
    )
    arg_parser.add_argument(
        '--keep-input-feature-data',
        dest='keep_input_feature_data',
        nargs='?',
        const=True,
        required=False,
        default=False
    )
    args = arg_parser.parse_args()

    Cleaner.clean(args.keep_project_data, args.keep_input_feature_data)
