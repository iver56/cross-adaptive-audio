import standardizer
import MultiNEAT as NEAT
import pickle
import effect


class LiveMapper(object):
    def __init__(self, parameter_data):
        self.parameter_data = parameter_data
        genotype = pickle.loads(self.parameter_data['genotype_pickled'])

        self.net = NEAT.NeuralNetwork()
        genotype.BuildPhenotype(self.net)

        self.standardizer = standardizer.Standardizer([])
        self.standardizer.feature_statistics = self.parameter_data['feature_statistics']

        self.effect = effect.get_effect_instance(self.parameter_data['args']['effect_names'])

        self.effect_parameters = None

    def activate(self, *analysis_vector):
        neural_input = self.standardize(analysis_vector)

        self.net.Flush()
        self.net.Input(neural_input)
        self.net.Activate()
        output = self.net.Output()
        neural_output = [min(1.0, max(0.0, x)) for x in output]

        self.scale_output(neural_output)

    def standardize(self, analysis_vector):
        neural_input = []
        for i, feature in enumerate(self.parameter_data['experiment_settings']['neural_input_channels']):
            neural_input.append(
                self.standardizer.get_standardized_value(feature, analysis_vector[i])
            )

        neural_input.append(1.0)  # bias
        return neural_input

    def scale_output(self, neural_output):
        self.effect_parameters = []
        # map neural output to the appropriate ranges of the effect parameters
        for i in range(self.effect.num_parameters):
            mapping = self.effect.parameters[i]['mapping']
            min_value = mapping['min_value']
            max_value = mapping['max_value']
            skew_factor = mapping['skew_factor']

            self.effect_parameters.append(
                standardizer.Standardizer.get_mapped_value(
                    normalized_value=neural_output[i],
                    min_value=min_value,
                    max_value=max_value,
                    skew_factor=skew_factor
                )
            )
        return self.effect_parameters

    def get_effect_parameter_value(self, i):
        return self.effect_parameters[int(i)]
