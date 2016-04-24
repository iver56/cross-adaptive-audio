import os
import settings
import json
import neural_network_representation
import pickle
import hashlib


class Individual(object):
    def __init__(self, genotype, generation, neural_input_mode, effect):
        self.genotype = genotype
        self.generation = generation
        self.output_sound = None
        self.neural_output_channels = None
        self.neural_input_mode = neural_input_mode
        self.effect = effect
        self.nn_representation = None

    def get_id(self):
        """
        state = self.genotype.__getstate__()
        pieces = state.split(' ')
        pieces = [pieces[i] for i in range(len(pieces)) if i != 5]  # remove ID at index 5
        state = ' '.join(pieces)
        return hashlib.md5(state.encode('utf-8')).hexdigest()
        """
        nn_repr = self.get_neural_network_representation()
        return hashlib.md5(json.dumps(nn_repr).encode('utf-8')).hexdigest()

    def get_individual_data_file_path(self):
        return os.path.join(
            settings.INDIVIDUAL_DATA_DIRECTORY,
            'individual_{}.json'.format(self.get_id())
        )

    def set_fitness(self, fitness):
        self.genotype.SetFitness(fitness)

    def set_output_sound(self, output_sound):
        self.output_sound = output_sound

    def set_neural_output(self, neural_output):
        self.neural_output_channels = neural_output

    def get_neural_network_representation(self):
        if self.nn_representation is None:
            self.nn_representation = neural_network_representation.get_neural_network_representation(
                nn=self.genotype,
                neural_input_mode=self.neural_input_mode,
                effect=self.effect,
                is_substrate=False
            )
        return self.nn_representation

    def get_neural_output_representation(self):
        series_standardized = {}
        for i in range(self.effect.num_parameters):
            parameter_key = self.effect.parameter_names[i]
            series_standardized[parameter_key] = self.neural_output_channels[i]
        return {
            'series_standardized': series_standardized,
            'ksmps': settings.CSOUND_KSMPS,
            'order': self.effect.parameter_names
        }

    def get_serialized_representation(self):
        """
        Get a serialized representation where data is included directly
        :return:
        """
        return {
            'id': self.get_id(),
            'fitness': self.genotype.GetFitness(),
            'neural_output': self.get_neural_output_representation(),
            'output_sound': self.output_sound.get_serialized_representation(),
            'neural_network_representation': self.get_neural_network_representation()
        }

    def get_short_serialized_representation(self):
        """
        Get a serialized representation with only references to data files
        :return:
        """
        return {
            'id': self.get_id(),
            'fitness': self.genotype.GetFitness()
        }

    def save(self):
        file_path = self.get_individual_data_file_path()
        data = self.get_serialized_representation()
        with settings.FILE_HANDLER(file_path, 'w') as outfile:
            json.dump(data, outfile)

    def delete(self, try_delete_serialized_representation=True):
        self.output_sound.delete()

        if try_delete_serialized_representation:
            try:
                os.remove(self.get_individual_data_file_path())
            except OSError:
                pass
