from __future__ import absolute_import
from jinja2 import Environment
import json


class TemplateHandler(object):
    def __init__(self, template_filename):
        self.template = None
        self.result = None
        self.env = Environment()
        self.init_custom_filters()
        with open(template_filename, 'r') as template_file:
            template_string = template_file.read()
            self.template = self.env.from_string(template_string)

    def init_custom_filters(self):
        self.env.filters['tojson'] = json.dumps

    def compile(self, *args, **kwargs):
        self.result = self.template.render(*args, **kwargs)
        return self.result

    def write_result(self, output_filename):
        with open(output_filename, "w") as output_file:
            output_file.write(self.result)
