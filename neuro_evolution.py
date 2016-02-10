from __future__ import absolute_import
import MultiNEAT as NEAT
import settings
import analyze
import cross_adapt
import argparse
import sound_file
import fitness_evaluator
import statistics


class NeuroEvolution(object):
    def __init__(self):
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument(
            '-i',
            '--input',
            dest='input_files',
            nargs='+',
            type=str,
            help='The filename of the parameter sound and the filename of the input sound, respectively',
            required=True,
            default=[]
        )
        args = arg_parser.parse_args()
        if len(args.input_files) == 2:
            self.param_sound = sound_file.SoundFile(args.input_files[0])
            self.input_sound = sound_file.SoundFile(args.input_files[1])
            self.num_frames = min(self.param_sound.get_num_frames(), self.input_sound.get_num_frames())

            self.param_input_vectors = []
            for k in range(self.num_frames):
                vector = self.param_sound.get_standardized_feature_vector(k)
                vector.append(1.0)  # bias input
                self.param_input_vectors.append(vector)
        else:
            raise Exception('Two filenames must be specified')

        self.run()

    def run(self):
        params = NEAT.Parameters()
        params.PopulationSize = 5  # TODO
        num_inputs = analyze.Analyzer.NUM_FEATURES + 1  # always add one extra input, see http://multineat.com/docs.html
        num_outputs = cross_adapt.CrossAdapter.NUM_PARAMETERS
        num_hidden_nodes = 0
        genome = NEAT.Genome(
            0,  # ID
            num_inputs,
            num_hidden_nodes,
            num_outputs,
            False,  # FS_NEAT
            NEAT.ActivationFunction.UNSIGNED_SIGMOID,  # OutputActType
            NEAT.ActivationFunction.UNSIGNED_SIGMOID,  # HiddenActType
            0,  # SeedType
            params  # Parameters
        )
        pop = NEAT.Population(
            genome,
            params,
            True,  # whether the population should be randomized
            1.0,  # how much the population should be randomized,
            settings.PRNG_SEED
        )

        for generation in range(3):  # TODO
            print('generation {}'.format(generation))
            # retrieve a list of all genomes in the population
            genome_list = NEAT.GetGenomeList(pop)

            fitness_list = []
            # apply the evaluation function to all genomes
            for genome in genome_list:
                fitness = self.evaluate(genome, generation)
                genome.SetFitness(fitness)
                fitness_list.append(fitness)

            avg_fitness = statistics.mean(fitness_list)
            print('avg_fitness: {}'.format(avg_fitness))

            # at this point we may output some information regarding the progress of evolution, best fitness, etc.
            # it's also the place to put any code that tracks the progress and saves the best genome or the entire
            # population. We skip all of this in the tutorial.

            # advance to the next generation
            pop.Epoch()

    def evaluate(self, genome, generation):
        # this creates a neural network (phenotype) from the genome
        net = NEAT.NeuralNetwork()
        genome.BuildPhenotype(net)  # TODO: How about BuildHyperNEATPhenotype instead

        output_vectors = []
        for input_vector in self.param_input_vectors:
            net.Input(input_vector)
            net.Activate()
            output = net.Output()
            output_vectors.append(list(output))

        resulting_sound = cross_adapt.CrossAdapter.cross_adapt(
            self.param_sound,
            self.input_sound,
            output_vectors,
            generation
        )

        fitness = fitness_evaluator.FitnessEvaluator.evaluate(self.param_sound, resulting_sound)
        return fitness

if __name__ == '__main__':
    NeuroEvolution()
