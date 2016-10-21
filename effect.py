import settings
import os
import json
import template_handler


class Effect(object):
    def __init__(self, name):
        self.template_dir = settings.EFFECT_DIRECTORY
        metadata_file_path = os.path.join(
            settings.EFFECT_DIRECTORY,
            '{}.json'.format(name)
        )

        try:
            with open(metadata_file_path) as data_file:
                try:
                    metadata = json.load(data_file)
                except ValueError:
                    raise Exception(
                        'Could not parse JSON file "{}".'
                        ' Please check that the JSON format/syntax is correct.'.format(
                            metadata_file_path
                        )
                    )
                self.parameters = metadata['parameters']
        except IOError:
            raise Exception(
                'Could not load {}. It doesn\'t exist. See effects/readme.txt for more info'.format(
                    metadata_file_path
                )
            )

        self.num_parameters = len(self.parameters)
        self.parameter_names = [p['name'] for p in self.parameters]
        self.name = name

    def get_template_handler(self, live=False):
        return template_handler.TemplateHandler(
            template_dir=self.template_dir,
            template_string=self.generate_template_string(live)
        )

    def generate_template_string(self, live=False):
        return '''
        {{% extends "{0}" %}}
        {{% block globals %}}
          {{% include "{1}.globals.jinja2" ignore missing %}}
        {{% endblock %}}
        {{% block effect %}}
          {{% include "{1}.effect.jinja2" %}}
        {{% endblock %}}
        '''.format(
            'base_template_live.csd.jinja2' if live else 'base_template.csd.jinja2',
            self.name
        )
