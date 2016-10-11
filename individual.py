import os
import settings
import json
import neural_network_representation
import hashlib
import experiment
import pickle  # TODO: try cPickle. it might be faster.


class Individual(object):
    def __init__(self, genotype, neural_input_mode, effect):
        self.genotype = genotype
        self.output_sound = None
        self.neural_output_channels = None
        self.neural_input_mode = neural_input_mode
        self.effect = effect
        self.nn_representation = None
        self.id = None
        self.born = None  # In which generation was this individual first discovered
        self.similarity = None  # may be different from the fitness value

    def get_id(self):
        """individuals with the same neural network have the same id"""
        if self.id is None:
            nn_repr = self.get_neural_network_representation()
            self.id = hashlib.md5(json.dumps(nn_repr).encode('utf-8')).hexdigest()
        return self.id

    def get_individual_data_file_path(self):
        return os.path.join(
            settings.INDIVIDUAL_DATA_DIRECTORY,
            experiment.Experiment.folder_name,
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
            'ksmps': settings.HOP_SIZE,
            'order': self.effect.parameter_names
        }

    def get_serialized_representation(self):
        """
        Get a serialized representation where data is included directly
        :return:
        """
        return {
            'id': self.get_id(),
            'similarity': self.similarity,
            'neural_output': self.get_neural_output_representation(),
            'output_sound': self.output_sound.get_serialized_representation(),
            'neural_network_representation': self.get_neural_network_representation(),
            'born': self.born,
            'genotype_pickled': pickle.dumps(self.genotype)
        }

    def get_short_serialized_representation(self):
        """
        Get a serialized representation with only references to data files
        :return:
        """
        return {
            'id': self.get_id(),
            'similarity': self.similarity,
            'fitness': self.genotype.GetFitness()
        }

    def save(self):
        file_path = self.get_individual_data_file_path()
        if os.path.exists(file_path):
            if settings.VERBOSE:
                print('individual {} already exists'.format(self.get_id()))
            return
        data = self.get_serialized_representation()
        with open(file_path, 'w') as outfile:
            json.dump(data, outfile)

    def delete(self, try_delete_serialized_representation=True):
        self.output_sound.delete()

        if try_delete_serialized_representation:
            try:
                os.remove(self.get_individual_data_file_path())
            except OSError:
                pass
