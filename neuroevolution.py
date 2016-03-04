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
import individual

try:
    import cv2
    import numpy as np
except:
    if settings.VERBOSE:
        print(
            'OpenCV + python bindings and/or numpy, which are required for visualization, could not be imported')


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
                '-g',
                '--num-generations',
                dest='num_generations',
                type=int,
                required=False,
                default=20
        )
        arg_parser.add_argument(
                '-p',
                '--population_size',
                dest='population_size',
                type=int,
                required=False,
                default=20
        )
        arg_parser.add_argument(
                '-s',
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
        arg_parser.add_argument(
                '--keep-only-best',
                nargs='?',
                dest='keep_only_best',
                help='Delete all sounds but the fittest in each generation',
                const=True,
                required=False,
                default=False
        )
        arg_parser.add_argument(
                '--allow-clones',
                nargs='?',
                dest='allow_clones',
                help="""Allow clones or nearly identical genomes to exist simultaneously in the
                    population. This is useful for non-deterministic environments,
                    as the same individual will get more than one chance to prove himself, also
                    there will be more chances the same individual to mutate in different ways.
                    The drawback is greatly increased time for reproduction. If you want to
                    search quickly, yet less efficient, leave this to true.""",
                const=True,
                required=False,
                default=False
        )
        arg_parser.add_argument(
                '--add-neuron-prob',
                dest='add_neuron_probability',
                type=float,
                help='MutateAddNeuronProb: Probability for a baby to be mutated with the'
                     ' Add-Neuron mutation',
                required=False,
                default=0.03
        )
        arg_parser.add_argument(
                '--add-link-prob',
                dest='add_link_probability',
                type=float,
                help='MutateAddLinkProb: Probability for a baby to be mutated with the'
                     ' Add-Link mutation',
                required=False,
                default=0.03
        )
        arg_parser.add_argument(
                '--rem-link-prob',
                dest='remove_link_probability',
                type=float,
                help='MutateRemLinkProb: Probability for a baby to be mutated with the'
                     ' Remove-Link mutation',
                required=False,
                default=0.03
        )
        arg_parser.add_argument(
                '--rem-simple-neuron-prob',
                dest='remove_simple_neuron_probability',
                type=float,
                help='MutateRemSimpleNeuronProb: Probability for a baby that a simple neuron'
                     ' will be replaced with a link',
                required=False,
                default=0.03
        )
        arg_parser.add_argument(
                '--fs-neat',
                nargs='?',
                dest='fs_neat',
                help='Use FS-NEAT',
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
            self.num_frames = min(self.param_sound.get_num_frames(),
                                  self.input_sound.get_num_frames())

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
        params.AllowClones = self.args.allow_clones
        params.MutateAddNeuronProb = self.args.add_neuron_probability
        params.MutateAddLinkProb = self.args.add_link_probability
        params.MutateRemLinkProb = self.args.remove_link_probability
        params.MutateRemSimpleNeuronProb = self.args.remove_simple_neuron_probability
        num_inputs = analyze.Analyzer.NUM_FEATURES + 1  # always add one extra input, see http://multineat.com/docs.html
        num_hidden_nodes = 0
        num_outputs = cross_adapt.CrossAdapter.NUM_PARAMETERS
        genome = NEAT.Genome(
                0,  # ID
                num_inputs,
                num_hidden_nodes,
                num_outputs,
                self.args.fs_neat,
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
            genotypes = NEAT.GetGenomeList(pop)

            individuals = []
            for genotype in genotypes:
                that_individual = individual.Individual(genotype, generation)
                fitness, output_sound = self.evaluate(that_individual, generation)
                that_individual.set_fitness(fitness)
                that_individual.set_output_sound(output_sound)
                that_individual.save()
                individuals.append(that_individual)
            individuals.sort(key=lambda i: i.genotype.GetFitness())

            flat_fitness_list = [i.genotype.GetFitness() for i in individuals]
            max_fitness = flat_fitness_list[-1]
            min_fitness = flat_fitness_list[0]
            print('best fitness: {0:.5f}'.format(max_fitness))
            avg_fitness = statistics.mean(flat_fitness_list)
            fitness_std_dev = statistics.pstdev(flat_fitness_list)
            print('avg fitness: {0:.5f}'.format(avg_fitness))
            stats_item = {
                'generation': generation,
                'fitness_min': min_fitness,
                'fitness_max': max_fitness,
                'fitness_avg': avg_fitness,
                'fitness_std_dev': fitness_std_dev,
                'individuals': [i.get_short_serialized_representation() for i in individuals]
            }
            self.stats_logger.data.append(stats_item)
            self.stats_logger.write()

            if self.args.visualize:
                net = NEAT.NeuralNetwork()
                individuals[-1].genotype.BuildPhenotype(net)  # build phenotype from best genotype
                img = np.zeros((500, 500, 3), dtype=np.uint8)
                NEAT.DrawPhenotype(img, (0, 0, 500, 500), net)
                cv2.imshow("NN", img)
                cv2.waitKey(1)

            if self.args.keep_only_best:
                # delete all but best fit results from this generation
                for i in range(len(individuals) - 1):
                    individuals[i].delete()  # delete the sound and its data

            # advance to the next generation
            pop.Epoch()
            print("Generation execution time: %s seconds" % (time.time() - generation_start_time))

    def evaluate(self, individual, generation):
        # this creates a neural network (phenotype) from the genome
        net = NEAT.NeuralNetwork()
        individual.genotype.BuildPhenotype(net)  # TODO: How about BuildHyperNEATPhenotype instead

        output_vectors = []
        for input_vector in self.param_input_vectors:
            net.Input(input_vector)
            net.Activate()
            output = net.Output()
            output_vectors.append(list(output))

        resulting_sound, resulting_neural_output = cross_adapt.CrossAdapter.cross_adapt(
                self.param_sound,
                self.input_sound,
                output_vectors,
                generation
        )
        resulting_sound.get_analysis(ensure_standardized_series=True)
        individual.set_neural_output(resulting_neural_output)

        fitness = fitness_evaluator.FitnessEvaluator.evaluate(self.param_sound, resulting_sound)
        return fitness, resulting_sound


if __name__ == '__main__':
    Neuroevolution()
