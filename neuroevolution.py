from __future__ import absolute_import
import MultiNEAT as NEAT
import settings
import analyze
import cross_adapt
import argparse
import sound_file
import fitness_evaluator
import statistics
import time
import logger
import os

try:
    import cv2
    import numpy as np
except:
    if settings.VERBOSE:
        print('OpenCV + python bindings and/or numpy, which are required for visualization, could not be imported')


class Neuroevolution(object):
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
        arg_parser.add_argument(
            '-g'
            '--num-generations',
            dest='num_generations',
            type=int,
            required=False,
            default=20
        )
        arg_parser.add_argument(
            '-p'
            '--population_size',
            dest='population_size',
            type=int,
            required=False,
            default=20
        )
        arg_parser.add_argument(
            '-s'
            '--seed',
            dest='seed',
            type=int,
            required=False,
            default=None
        )
        arg_parser.add_argument(
            '-v',
            '--visualize',
            nargs='?',
            dest='visualize',
            help='Visualize the best neural network in each generation',
            const=True,
            required=False,
            default=False
        )
        self.args = arg_parser.parse_args()

        if self.args.seed is not None:
            settings.PRNG_SEED = self.args.seed

        if len(self.args.input_files) == 2:
            self.param_sound = sound_file.SoundFile(self.args.input_files[0])
            self.input_sound = sound_file.SoundFile(self.args.input_files[1])
            self.num_frames = min(self.param_sound.get_num_frames(), self.input_sound.get_num_frames())

            self.param_input_vectors = []
            for k in range(self.num_frames):
                vector = self.param_sound.get_standardized_feature_vector(k)
                vector.append(1.0)  # bias input
                self.param_input_vectors.append(vector)
        else:
            raise Exception('Two filenames must be specified')

        self.stats_logger = logger.Logger(
            os.path.join(settings.STATS_DATA_DIRECTORY, 'stats.json'),
            suppress_initialization=True
        )
        self.stats_logger.data = []

        self.run()

    def run(self):
        params = NEAT.Parameters()
        params.PopulationSize = self.args.population_size
        num_inputs = analyze.Analyzer.NUM_FEATURES + 1  # always add one extra input, see http://multineat.com/docs.html
        num_hidden_nodes = 0
        num_outputs = cross_adapt.CrossAdapter.NUM_PARAMETERS
        genome = NEAT.Genome(
            0,  # ID
            num_inputs,
            num_hidden_nodes,
            num_outputs,
            False,  # FS_NEAT
            NEAT.ActivationFunction.UNSIGNED_SIGMOID,  # OutputActType
            NEAT.ActivationFunction.TANH,  # HiddenActType
            0,  # SeedType
            params  # Parameters
        )
        pop = NEAT.Population(
            genome,
            params,
            True,  # whether the population should be randomized
            2.0,  # how much the population should be randomized,
            settings.PRNG_SEED
        )

        for generation in range(1, self.args.num_generations + 1):
            generation_start_time = time.time()
            print('generation {}'.format(generation))
            # retrieve a list of all genomes in the population
            genome_list = NEAT.GetGenomeList(pop)

            fitness_list = []
            # apply the evaluation function to all genomes
            for genome in genome_list:
                fitness, output_sound = self.evaluate(genome, generation)
                genome.SetFitness(fitness)
                fitness_list.append((fitness, genome, output_sound))
            fitness_list.sort(reverse=True)

            fitness_list_flat = [x[0] for x in fitness_list]
            max_fitness = fitness_list_flat[0]
            print('best fitness: {0:.5f}'.format(max_fitness))
            avg_fitness = statistics.mean(fitness_list_flat)
            fitness_std_dev = statistics.pstdev(fitness_list_flat)
            print('avg fitness: {0:.5f}'.format(avg_fitness))
            stats_item = {
                'generation': generation,
                'fitness_max': max_fitness,
                'fitness_avg': avg_fitness,
                'fitness_std_dev': fitness_std_dev
            }
            self.stats_logger.data.append(stats_item)
            self.stats_logger.write()

            if self.args.visualize:
                net = NEAT.NeuralNetwork()
                fitness_list[0][1].BuildPhenotype(net)
                img = np.zeros((500, 500, 3), dtype=np.uint8)
                NEAT.DrawPhenotype(img, (0, 0, 500, 500), net)
                cv2.imshow("NN", img)
                cv2.waitKey(1)

            # delete all but best fit results from this generation
            for i in range(1, len(fitness_list)):
                fitness_list[i][2].delete()  # delete the sound and its data

            # TODO: store genome

            # advance to the next generation
            pop.Epoch()
            print("Generation execution time: %s seconds" % (time.time() - generation_start_time))

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
        resulting_sound.get_analysis(ensure_standardized_series=True)

        fitness = fitness_evaluator.FitnessEvaluator.evaluate(self.param_sound, resulting_sound)
        return fitness, resulting_sound

if __name__ == '__main__':
    Neuroevolution()
