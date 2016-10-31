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


class CompositeEffect(object):
    def __init__(self, effect_names):
        if len(effect_names) == 0:
            raise Exception('At least one effect must be specified')

        self.template_dir = settings.EFFECT_DIRECTORY
        self.effect_names = effect_names
        self.effects = [Effect(name) for name in effect_names]

        self.parameter_names = []
        self.parameters = []
        for effect in self.effects:
            self.parameters += effect.parameters
            self.parameter_names += effect.parameter_names

        self.num_parameters = sum(effect.num_parameters for effect in self.effects)

        self.name = 'composite'

    def get_template_handler(self, live=False):
        return template_handler.TemplateHandler(
            template_dir=self.template_dir,
            template_string=self.generate_template_string(live)
        )

    def generate_template_string(self, live=False):
        template_template_file_path = os.path.join(settings.EFFECT_DIRECTORY, 'composite.jinja2')
        with open(template_template_file_path, 'r') as template_file:
            template_template_string = template_file.read()

        that_template_handler = template_handler.TemplateHandler(
            template_dir=self.template_dir,
            template_string=template_template_string
        )

        base_template = 'base_template_live.csd.jinja2' if live else 'base_template.csd.jinja2'
        return that_template_handler.compile(
            base_template=base_template,
            effects=self.effects
        )
