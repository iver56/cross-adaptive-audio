from jinja2 import Template


class TemplateHandler(object):
    def __init__(self, template_filename):
        self.template = None
        self.result = None
        with open(template_filename, 'r') as template_file:
            template_string = template_file.read()
            self.template = Template(template_string)

    def compile(self, *args, **kwargs):
        self.result = self.template.render(*args, **kwargs)
        return self.result

    def write_result(self, output_filename):
        with open(output_filename, "w") as output_file:
            output_file.write(self.result)
