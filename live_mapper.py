import standardizer
import MultiNEAT as NEAT
import json
import pickle
import effect
import create_live_csd


class LiveMapper(object):
    def __init__(self, individual_id):
        _, stats_file_path, individual_data_file_path = create_live_csd.resolve_paths(individual_id)
        with open(stats_file_path, 'r') as data_file:
            self.project_data = json.load(data_file)

        with open(individual_data_file_path, 'r') as data_file:
            individual_data = json.load(data_file)

        genotype = pickle.loads(individual_data['genotype_pickled'])

        self.net = NEAT.NeuralNetwork()
        genotype.BuildPhenotype(self.net)

        self.standardizer = standardizer.Standardizer([])
        self.standardizer.feature_statistics = self.project_data['feature_statistics']

        self.effect = effect.Effect.get_effect_by_name(self.project_data['args']['effect_name'])

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
        for i, feature in enumerate(self.project_data['experiment_settings']['neural_input_channels']):
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
