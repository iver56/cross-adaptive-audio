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
import project
import effect


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
            '--patience',
            dest='patience',
            help='Number of generations with no improvement before stopping',
            type=int,
            required=False,
            default=5
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
            '--keep-k-best',
            nargs='?',
            dest='keep_k_best',
            help='Store only the k fittest individual in each generation. Improves perf and saves storage',
            type=int,
            required=False,
            default=-1  # -1 means keep all
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
            default=0.06
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
        arg_parser.add_argument(
            '--neural-input-mode',
            dest='neural_input_mode',
            type=str,
            choices=['a', 'ab', 'b', 's'],
            help='What to use as neural input. Mode a: target sound. Mode ab: target sound and'
                 ' input sound. Mode b: input sound. Mode s: static input, i.e. only bias.',
            required=False,
            default="a"
        )
        arg_parser.add_argument(
            '--fitness',
            dest='fitness',
            type=str,
            help='Multi-Objective (mo) fitness optimizes for a diverse'
                 ' population that consists of various non-dominated trade-offs between similarity'
                 ' in different features',
            choices=['default', 'mo'],
            required=False,
            default="default"
        )
        arg_parser.add_argument(
            '--effect',
            dest='effect_name',
            type=str,
            help='The name of the sound effect to use. See the effects folder for options.',
            required=False,
            default="dist_lpf"
        )
        self.args = arg_parser.parse_args()

        if self.args.keep_k_best == 0 or self.args.keep_k_best > self.args.population_size:
            raise Exception('keep-k-best must be positive and not greater than the population size')

        if self.args.seed is not None:
            settings.PRNG_SEED = self.args.seed

        if len(self.args.input_files) != 2:
            raise Exception('Two filenames must be specified')

        self.target_sound = sound_file.SoundFile(self.args.input_files[0])
        self.input_sound = sound_file.SoundFile(self.args.input_files[1])

        self.project = project.Project([self.target_sound, self.input_sound])
        self.analyzer = analyze.Analyzer(self.project)
        self.fitness_evaluator_class = None
        if self.args.fitness == 'default':
            self.fitness_evaluator_class = fitness_evaluator.FitnessEvaluator
        elif self.args.fitness == 'mo':
            self.fitness_evaluator_class = fitness_evaluator.MultiObjectiveFitnessEvaluator

        self.num_frames = min(
            self.target_sound.get_num_frames(),
            self.input_sound.get_num_frames()
        )

        self.neural_input_vectors = []
        if self.args.neural_input_mode == 'a':
            for k in range(self.num_frames):
                vector = self.target_sound.get_standardized_neural_input_vector(k)
                vector.append(1.0)  # bias input
                self.neural_input_vectors.append(vector)
        elif self.args.neural_input_mode == 'ab':
            for k in range(self.num_frames):
                vector = self.target_sound.get_standardized_neural_input_vector(k)
                vector += self.input_sound.get_standardized_neural_input_vector(k)
                vector.append(1.0)  # bias input
                self.neural_input_vectors.append(vector)
        elif self.args.neural_input_mode == 'b':
            for k in range(self.num_frames):
                vector = self.input_sound.get_standardized_neural_input_vector(k)
                vector.append(1.0)  # bias input
                self.neural_input_vectors.append(vector)
        elif self.args.neural_input_mode == 's':
            self.args.add_neuron_probability = 0.0
            for k in range(self.num_frames):
                vector = [1.0]  # bias input
                self.neural_input_vectors.append(vector)

        self.effect = effect.Effect.get_effect_by_name(self.args.effect_name)
        self.cross_adapter = cross_adapt.CrossAdapter(
            input_sound=self.input_sound,
            neural_input_vectors=self.neural_input_vectors,
            effect=self.effect,
            parameter_lpf_cutoff=settings.PARAMETER_LPF_CUTOFF
        )

        self.stats_logger = logger.Logger(
            os.path.join(settings.STATS_DATA_DIRECTORY, 'stats.json'),
            suppress_initialization=True
        )
        self.stats_logger.data = {
            'param_sound': self.target_sound.get_serialized_representation(),
            'input_sound': self.input_sound.get_serialized_representation(),
            'generations': []
        }
        self.max_fitness = None
        self.last_fitness_improvement = 0  # generation number
        if self.args.keep_k_best != -1:
            self.best_individual_ids = set()

        self.individual_fitness = {}  # individual id => individual fitness

        self.population = None
        self.init_neat()

        run_start_time = time.time()
        self.run()
        print("Run execution time: {0:.2f} seconds".format(time.time() - run_start_time))

    def has_patience_ended(self, max_fitness, generation):
        """
        Return True if patience has ended, i.e. too many generations have passed without
        improving max fitness
        """
        if self.max_fitness is None or max_fitness > self.max_fitness:
            self.max_fitness = max_fitness
            self.last_fitness_improvement = generation
            return False  # There is progress. Keep going.
        elif generation - self.last_fitness_improvement >= self.args.patience:
            return True  # Patience has ended. Stop evolving.

    def init_neat(self):
        params = NEAT.Parameters()
        params.PopulationSize = self.args.population_size
        params.AllowClones = self.args.allow_clones
        params.MutateAddNeuronProb = self.args.add_neuron_probability
        params.MutateAddLinkProb = self.args.add_link_probability
        params.MutateRemLinkProb = self.args.remove_link_probability
        params.MutateRemSimpleNeuronProb = self.args.remove_simple_neuron_probability
        num_inputs = len(self.neural_input_vectors[0])
        num_hidden_nodes = 0
        num_outputs = self.effect.num_parameters
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
        self.population = NEAT.Population(
            genome,
            params,
            True,  # whether the population should be randomized
            2.0,  # how much the population should be randomized,
            settings.PRNG_SEED
        )

    def run(self):
        for generation in range(1, self.args.num_generations + 1):
            generation_start_time = time.time()
            print('generation {}'.format(generation))

            # Retrieve a list of all genomes in the population
            genotypes = NEAT.GetGenomeList(self.population)

            individuals = []
            all_individuals = []
            for genotype in genotypes:
                that_individual = individual.Individual(
                    genotype=genotype,
                    generation=generation,
                    neural_input_mode=self.args.neural_input_mode,
                    effect=self.effect
                )

                if (not self.fitness_evaluator_class.IS_FITNESS_RELATIVE) and \
                                that_individual.get_id() in self.individual_fitness:
                    if settings.VERBOSE:
                        print(that_individual.get_id() + ' already exists. Will not evaluate again')

                    that_individual.set_fitness(self.individual_fitness[that_individual.get_id()])
                else:
                    individuals.append(that_individual)
                all_individuals.append(that_individual)

            # Check for duplicate individuals
            duplicates = {}
            unique_individuals = {}
            for ind in individuals:
                if ind.get_id() in unique_individuals:
                    if ind.get_id() in duplicates:
                        duplicates[ind.get_id()].append(ind)
                    else:
                        duplicates[ind.get_id()] = [ind]
                else:
                    unique_individuals[ind.get_id()] = ind
            if settings.VERBOSE and len(duplicates):
                print('duplicates', duplicates)

            unique_individuals_list = [unique_individuals[ind_id] for ind_id in unique_individuals]

            # Produce sound files for each unique individual
            self.cross_adapter.produce_output_sounds(unique_individuals_list)

            # Evaluate fitness of each unique individual
            self.evaluate_fitness(unique_individuals_list)

            # Set analysis and fitness on duplicates
            for individual_id in duplicates:
                for ind in duplicates[individual_id]:
                    ind.set_output_sound(unique_individuals[individual_id].output_sound)
                    if self.args.fitness == 'mo':
                        # Discourage clusters of duplicates
                        ind.set_fitness(
                            0.5 * unique_individuals[individual_id].genotype.GetFitness()
                        )
                    else:
                        ind.set_fitness(unique_individuals[individual_id].genotype.GetFitness())

            # Calculate and write stats
            all_individuals.sort(key=lambda i: i.genotype.GetFitness())
            flat_fitness_list = [i.genotype.GetFitness() for i in all_individuals]
            max_fitness = flat_fitness_list[-1]
            min_fitness = flat_fitness_list[0]
            print('max fitness: {0:.5f}'.format(max_fitness))
            avg_fitness = statistics.mean(flat_fitness_list)
            fitness_std_dev = statistics.pstdev(flat_fitness_list)
            print('avg fitness: {0:.5f}'.format(avg_fitness))
            stats_item = {
                'generation': generation,
                'fitness_min': min_fitness,
                'fitness_max': max_fitness,
                'fitness_avg': avg_fitness,
                'fitness_std_dev': fitness_std_dev,
                'individuals': [i.get_short_serialized_representation() for i in all_individuals]
            }
            self.stats_logger.data['generations'].append(stats_item)
            self.stats_logger.write()

            # Store individual(s)
            if self.args.keep_k_best != -1:
                unique_individuals_list.sort(key=lambda i: i.genotype.GetFitness(), reverse=True)
                for i in range(self.args.keep_k_best):
                    self.best_individual_ids.add(unique_individuals_list[i].get_id())
                    unique_individuals_list[i].save()

                # delete all but best fit results from this generation
                for i in range(self.args.keep_k_best, len(unique_individuals_list)):
                    if unique_individuals_list[i].get_id() not in self.best_individual_ids:
                        unique_individuals_list[i].delete(
                            try_delete_serialized_representation=False)
            else:
                # keep all individuals
                for that_individual in unique_individuals_list:
                    individual_id = that_individual.get_id()
                    if individual_id not in self.individual_fitness:
                        that_individual.save()
                    self.individual_fitness[individual_id] = that_individual.genotype.GetFitness()

            if (not self.fitness_evaluator_class.IS_FITNESS_RELATIVE) and \
                    self.has_patience_ended(max_fitness, generation):
                print(
                    'Patience has ended because max fitness has not improved for {} generations.'
                    ' Stopping.'.format(self.args.patience)
                )
                break
                # TODO: implement patience for multi-objective fitness

            # advance to the next generation
            self.population.Epoch()
            print("Generation execution time: {0:.2f} seconds".format(
                time.time() - generation_start_time)
            )

    def evaluate_fitness(self, individuals):
        sound_files_to_analyze = [
            that_individual.output_sound for that_individual in individuals
            ]
        self.analyzer.analyze_multiple(sound_files_to_analyze)

        self.fitness_evaluator_class.evaluate_multiple(
            individuals,
            self.target_sound
        )


if __name__ == '__main__':
    Neuroevolution()
