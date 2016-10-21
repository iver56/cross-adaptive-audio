from __future__ import absolute_import
from jinja2 import Environment, FileSystemLoader
import json
import inspect
import os


class TemplateHandler(object):
    def __init__(self, template_file_path, template_string=None, transform_template_string=None):
        self.template = None
        self.result = None
        dir_name = os.path.dirname(template_file_path)
        self.env = Environment(
            loader=FileSystemLoader(searchpath=dir_name)
        )
        self.init_custom_filters()

        if template_string is None:
            with open(template_file_path, 'r') as template_file:
                template_string = template_file.read()

        if inspect.isfunction(transform_template_string):
            template_string = transform_template_string(template_string)

        self.template = self.env.from_string(template_string)

    def init_custom_filters(self):
        self.env.filters['tojson'] = json.dumps

    def compile(self, *args, **kwargs):
        self.result = self.template.render(*args, **kwargs)
        return self.result

    def write_result(self, output_filename):
        with open(output_filename, "w") as output_file:
            output_file.write(self.result)

