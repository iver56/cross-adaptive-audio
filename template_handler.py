from __future__ import absolute_import
from jinja2 import Environment, FileSystemLoader
import json
import inspect
import os


class TemplateHandler(object):
    def __init__(self, template_dir, template_string):
        self.template = None
        self.result = None
        self.env = Environment(
            loader=FileSystemLoader(searchpath=template_dir)
        )
        self.init_custom_filters()

        self.template = self.env.from_string(template_string)

    def init_custom_filters(self):
        self.env.filters['tojson'] = json.dumps

    def compile(self, *args, **kwargs):
        self.result = self.template.render(*args, **kwargs)
        return self.result

    def write_result(self, output_filename):
        with open(output_filename, "w") as output_file:
            output_file.write(self.result)

