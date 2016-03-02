import pprint
import inspect
import os
import settings


class Individual(object):
    def __init__(self, genotype, generation):
        self.genotype = genotype
        self.generation = generation
        #pprint.pprint(inspect.getmembers(genotype))
        self.id = genotype.GetID()
        self.output_sound = None
        self.neural_output = None

    def get_individual_data_file_path(self):
        return os.path.join(
                settings.INDIVIDUAL_DATA_DIRECTORY,
                'individual_{}.json'.format(self.id)
        )

    def get_genome_data_file_path(self):
        return os.path.join(
                settings.GENOTYPE_DATA_DIRECTORY,
                'genotype_{}.txt'.format(self.id)
        )

    def save_genotype_data_file(self):
        self.genotype.Save(self.get_genome_data_file_path())

    def set_fitness(self, fitness):
        self.genotype.SetFitness(fitness)

    def set_output_sound(self, output_sound):
        self.output_sound = output_sound

    def set_neural_output(self, neural_output):
        self.neural_output = neural_output
