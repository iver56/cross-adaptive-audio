import settings
import os
import json


class Effect(object):
    def __init__(self, template_file_path, parameters):
        self.template_file_path = template_file_path
        self.parameters = parameters
        self.num_parameters = len(parameters)
        self.parameter_names = [p['name'] for p in parameters]

    @staticmethod
    def get_effect_by_name(name):
        template_file_path = os.path.join(settings.EFFECT_DIRECTORY, '{}.csd.jinja2'.format(name))
        metadata_file_path = os.path.join(settings.EFFECT_DIRECTORY, '{}.json'.format(name))

        try:
            with open(metadata_file_path) as data_file:
                metadata = json.load(data_file)
                parameters = metadata['parameters']
                return Effect(template_file_path, parameters)
        except IOError:
            raise Exception(
                'Could not load {}. It doesn\'t exist. See effects/readme.txt for more info'.format(
                    metadata_file_path
                )
            )
