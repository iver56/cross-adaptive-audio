from __future__ import absolute_import
from __future__ import print_function
import settings
import os
import argparse
import shutil


class Cleaner(object):
    @staticmethod
    def clean(keep_project_data=True, keep_input_feature_data=True, keep_output_sounds=True, ensure_directories=False):
        """
        Remove feature data and meta data cache
        :param keep_project_data:
        :param keep_input_feature_data:
        :param keep_output_sounds:
        :param ensure_directories:
        :return:
        """
        paths = [
            settings.OUTPUT_FEATURE_DATA_DIRECTORY,
            settings.CSD_DIRECTORY,
            settings.NEURAL_OUTPUT_DIRECTORY
        ]
        extensions = ['.json', '.csd']
        if not keep_input_feature_data:
            paths.append(settings.INPUT_FEATURE_DATA_DIRECTORY)
            paths.append(settings.META_DATA_CACHE_DIRECTORY)
        if not keep_project_data:
            paths.append(settings.PROJECT_DATA_DIRECTORY)
        if not keep_output_sounds:
            paths.append(settings.OUTPUT_DIRECTORY)
            extensions.append('.wav')

        for path in paths:
            for root, dirs, files in os.walk(path):
                for currentFile in files:
                    if any(currentFile.lower().endswith(ext) for ext in extensions):
                        print("Removing file: " + currentFile)
                        os.remove(os.path.join(root, currentFile))

        if ensure_directories:
            all_paths = [
                settings.CSD_DIRECTORY,
                settings.INPUT_FEATURE_DATA_DIRECTORY,
                settings.OUTPUT_FEATURE_DATA_DIRECTORY,
                settings.NEURAL_OUTPUT_DIRECTORY,
                settings.INPUT_DIRECTORY,
                settings.META_DATA_CACHE_DIRECTORY,
                settings.OUTPUT_DIRECTORY,
                settings.PROJECT_DATA_DIRECTORY,
                settings.STATS_DATA_DIRECTORY
            ]

            for path in all_paths:
                if not os.path.exists(path):
                    print('Creating directory {}'.format(path))
                    os.makedirs(path)

            if settings.USE_RAM_DISK:
                print('Copying test audio files to input folder in RAM disk')
                filenames = [
                    f for f in os.listdir(settings.TEST_AUDIO_DIRECTORY)
                    if os.path.isfile(os.path.join(settings.TEST_AUDIO_DIRECTORY, f))
                    ]
                filenames = [filename for filename in filenames if
                             filename.split('.')[-1] in settings.WHITELISTED_SOUND_FILE_EXTENSIONS]
                for filename in filenames:
                    print(filename)
                    shutil.copyfile(
                        os.path.join(settings.TEST_AUDIO_DIRECTORY, filename),
                        os.path.join(settings.INPUT_DIRECTORY, filename)
                    )


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
    arg_parser.add_argument(
        '--keep-output-sounds',
        dest='keep_output_sounds',
        nargs='?',
        const=True,
        required=False,
        default=False
    )
    arg_parser.add_argument(
        '--ensure-directories',
        dest='ensure_directories',
        nargs='?',
        const=True,
        required=False,
        default=False
    )

    args = arg_parser.parse_args()

    Cleaner.clean(
        args.keep_project_data,
        args.keep_input_feature_data,
        args.keep_output_sounds,
        args.ensure_directories
    )
