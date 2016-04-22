import pprint
# import inspect
import os
import settings
import json
import neural_network_representation
import cross_adapt


class Individual(object):
    def __init__(self, genotype, generation):
        self.genotype = genotype
        self.generation = generation
        # pprint.pprint(inspect.getmembers(genotype))
        self.id = genotype.GetID()
        self.output_sound = None
        self.neural_output = None

    def get_individual_data_file_path(self):
        return os.path.join(
                settings.INDIVIDUAL_DATA_DIRECTORY,
                'individual_{}.json'.format(self.id)
        )

    def set_fitness(self, fitness):
        self.genotype.SetFitness(fitness)

    def set_output_sound(self, output_sound):
        self.output_sound = output_sound

    def set_neural_output(self, neural_output):
        self.neural_output = neural_output

    def get_neural_network_representation(self):
        return neural_network_representation.get_neural_network_representation(
                self.genotype
        )

    def get_neural_output_representation(self):
        channels = self.neural_output.channels
        series_standardized = {}
        for i in range(len(cross_adapt.CrossAdapter.PARAMETER_LIST)):
            parameter = cross_adapt.CrossAdapter.PARAMETER_LIST[i]
            series_standardized[parameter] = channels[i]
        return {
            'series_standardized': series_standardized,
            'ksmps': settings.CSOUND_KSMPS,
            'order': cross_adapt.CrossAdapter.PARAMETER_LIST
        }

    def get_serialized_representation(self):
        """
        Get a serialized representation where data is included directly
        :return:
        """
        return {
            'id': self.output_sound.get_md5(),
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
            'id': self.output_sound.get_md5(),
            'fitness': self.genotype.GetFitness()
        }

    def save(self):
        file_path = self.get_individual_data_file_path()
        data = self.get_serialized_representation()
        with settings.FILE_HANDLER(file_path, 'w') as outfile:
            json.dump(data, outfile)

    def delete(self):
        self.output_sound.delete()
        self.neural_output.delete()

        try:
            os.remove(self.get_individual_data_file_path())
        except OSError:
            pass
