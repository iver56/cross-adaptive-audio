from __future__ import absolute_import
from __future__ import print_function
import argparse
import settings
from os import listdir
from os.path import isfile, join
import re
import json
import sound_file
import standardizer


class CreateProject(object):
    WHITELISTED_FILE_EXTENSIONS = ['wav']

    def __init__(self):
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument(
            '-n',
            '--name',
            dest='name',
            required=True,
            help='The name of the project',
            default=''
        )
        arg_parser.add_argument(
            '-i',
            '--input',
            dest='input_files',
            nargs='+',
            type=str,
            help='The names of the sound files to be included/processed in the project',
            required=False,
            default=[]
        )
        arg_parser.add_argument(
            '-s',
            '--subfolder',
            dest='subfolder',
            required=False,
            help='You may use this instead of specifying a list of files. With this flag, all sound files in'
                 ' the the given subfolder in the input folder will be added to the project',
            default=''
        )
        self.args = arg_parser.parse_args()
        self.project_data = {
            'name': self.args.name,
            'filenames': [],
            'feature_statistics': None
        }
        self.sound_files = None

        self.create_project()
        self.analyze_all()
        self.standardize_analyses()
        self.write_project_data()

    @staticmethod
    def clean_string(string):
        string = string.lower()
        string = re.sub(r'[^\w ]+', '', string)
        string = re.sub(r' +', '-', string)
        return string

    def create_project(self):
        if len(self.args.input_files) > 0:
            self.project_data['filenames'] = self.args.input_files
        else:
            self.project_data['filenames'] = [
                join(self.args.subfolder, f) for f in listdir(settings.INPUT_DIRECTORY)
                if isfile(join(settings.INPUT_DIRECTORY, self.args.subfolder, f))
                ]

        self.project_data['filenames'] = [filename for filename in self.project_data['filenames'] if filename.split('.')[-1] in self.WHITELISTED_FILE_EXTENSIONS]
        if len(self.project_data['filenames']) == 0:
            raise Exception('No sound files added to the project')

    def analyze_all(self):
        print('Analyzing all sound files in project...')
        self.sound_files = []
        for filename in self.project_data['filenames']:
            print('Analyzing "{}"...'.format(filename))
            sf = sound_file.SoundFile(filename)
            sf.get_analysis()
            self.sound_files.append(sf)

    def standardize_analyses(self):
        print('Calculating standardization parameters...')
        s = standardizer.Standardizer(self.sound_files)
        s.calculate_feature_statistics()
        self.project_data['feature_statistics'] = s.feature_statistics
        s.add_standardized_series()

    def write_project_data(self):
        project_json_filename = self.clean_string(self.project_data['name']) + '.json'
        project_file_path = join(settings.PROJECT_DATA_DIRECTORY, project_json_filename)
        with settings.FILE_HANDLER(project_file_path, 'wb') as outfile:
            json.dump(self.project_data, outfile)
        print('Created project file', project_json_filename, \
            'with', len(self.project_data['filenames']), 'sound file(s)')

if __name__ == '__main__':
    CreateProject()
