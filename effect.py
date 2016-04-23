class Effect(object):
    def __init__(self, template_filename, parameters):
        self.template_filename = template_filename
        self.parameters = parameters
        self.num_parameters = len(parameters)
        self.parameter_names = [p['name'] for p in parameters]

effects = {
    'dist_lpf': Effect(
        template_filename='dist_lpf.csd.jinja2',
        parameters=[
            {
                'name': 'drive',
                'mapping': {
                    'min': 1.0,
                    'max': 12.0,
                    'skew_factor': 1.0
                }
            },
            {
                'name': 'freq',
                'mapping': {
                    'min': 20.0,
                    'max': 10000.0,
                    'skew_factor': 0.3
                }
            },
            {
                'name': 'resonance',
                'mapping': {
                    'min': 0.001,
                    'max': 0.95,
                    'skew_factor': 1.0
                }
            },
            {
                'name': 'dist',
                'mapping': {
                    'min': 0.001,
                    'max': 10,
                    'skew_factor': 0.5
                }
            },
            {
                'name': 'mix',
                'mapping': {
                    'min': 0.0,
                    'max': 1.0,
                    'skew_factor': 1.0
                }
            },
            {
                'name': 'post_gain',
                'mapping': {
                    'min': 0.0,
                    'max': 3.16227,
                    'skew_factor': 0.3
                }
            }
        ]
    )
}
