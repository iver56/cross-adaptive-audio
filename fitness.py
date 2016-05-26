from __future__ import print_function
import math
import settings
import experiment
import random
import numpy as np


class AbstractFitness(object):
    # Whether or not fitness is relative, i.e. it changes from generation to generation
    # and/or depends on (the fitness of) other individuals
    IS_FITNESS_RELATIVE = False

    def __init__(self, target_sound):
        self.target_sound = target_sound

    def evaluate_multiple(self, individuals):
        raise Exception('evaluate_multiple must be implemented by the subclass')


class LocalSimilarityFitness(AbstractFitness):
    IS_FITNESS_RELATIVE = False

    def evaluate_multiple(self, individuals):
        fitness_values = []
        for ind in individuals:
            fitness = LocalSimilarityFitness.get_local_similarity(
                self.target_sound,
                ind.output_sound
            )
            fitness_values.append(fitness)
        return fitness_values

    @staticmethod
    def get_local_similarity(param_sound, output_sound):
        """
        How much does sound_file_c sound like sound_file_a
        :param param_sound: SoundFile instance
        :param output_sound: SoundFile instance
        :return:
        """
        euclidean_distance_sum = 0
        for k in range(param_sound.get_num_frames()):
            sum_of_squared_differences = 0
            for feature in experiment.SIMILARITY_CHANNELS:
                param_value = param_sound.analysis['series_standardized'][feature][k]
                try:
                    output_value = output_sound.analysis['series_standardized'][feature][k]
                except IndexError:
                    print('Tried to get feature {0} of output sound at k index {1}'.format(
                        feature,
                        k
                    ))
                    print('Feature series lengths:')
                    for that_feature in output_sound.analysis['series_standardized']:
                        print(
                            that_feature,
                            len(output_sound.analysis['series_standardized'][that_feature])
                        )
                    raise

                sum_of_squared_differences += experiment.SIMILARITY_WEIGHTS[feature] * \
                                              (param_value - output_value) ** 2
            euclidean_distance = math.sqrt(sum_of_squared_differences)
            euclidean_distance_sum += euclidean_distance

        average_euclidean_distance = euclidean_distance_sum / param_sound.get_num_frames()

        if settings.VERBOSE:
            print('local_stats_average_distance', average_euclidean_distance)

        return 1.0 / (1.0 + average_euclidean_distance)

    @staticmethod
    def get_euclidean_distance(vector_a, vector_b):
        sum_of_squared_differences = 0
        for i in range(len(vector_a)):
            sum_of_squared_differences += (vector_b[i] - vector_a[i]) ** 2

        return math.sqrt(sum_of_squared_differences)


class MultiObjectiveFitness(AbstractFitness):
    IS_FITNESS_RELATIVE = True

    @staticmethod
    def calculate_objectives(that_individual, target_sound):
        that_individual.objectives = {}
        for feature in experiment.SIMILARITY_CHANNELS:
            sum_of_squared_differences = 0
            for k in range(target_sound.get_num_frames()):
                param_value = target_sound.analysis['series_standardized'][feature][k]
                output_value = \
                    that_individual.output_sound.analysis['series_standardized'][feature][k]
                sum_of_squared_differences += (param_value - output_value) ** 2
            euclidean_distance = math.sqrt(sum_of_squared_differences)
            that_individual.objectives[feature] = euclidean_distance

    @staticmethod
    def individual_dominates(first_individual, other_individual):
        for feature in first_individual.objectives:
            if other_individual.objectives[feature] < first_individual.objectives[feature]:
                return False

        for feature in first_individual.objectives:
            if first_individual.objectives[feature] < other_individual.objectives[feature]:
                return True
        return False

    @staticmethod
    def fast_non_dominated_sort(individuals):
        """
        After having run this, each individual is assigned a rank (1 is best, higher is worse)
        The function returns a "fronts" dictionary which contains a set of individuals for each rank
        """
        fronts = {
            1: set()
        }
        for p in individuals:
            p.individuals_dominated = set()
            p.domination_counter = 0
            for q in individuals:
                if MultiObjectiveFitness.individual_dominates(p, q):
                    p.individuals_dominated.add(q)
                elif MultiObjectiveFitness.individual_dominates(q, p):
                    p.domination_counter += 1
            if p.domination_counter == 0:
                p.rank = 1
                fronts[1].add(p)
        i = 1
        while len(fronts[i]) != 0:
            new_front = set()
            for p in fronts[i]:
                for q in p.individuals_dominated:
                    q.domination_counter -= 1
                    if q.domination_counter == 0:
                        q.rank = i + 1
                        new_front.add(q)
            i += 1
            fronts[i] = new_front
        return fronts

    @staticmethod
    def calculate_crowding_distances(front):
        """
        front is a list of individuals
        """
        if len(front) == 0:
            return

        for ind in front:
            ind.crowding_distance = 0.0

        for feature in experiment.SIMILARITY_CHANNELS:
            front = sorted(front, key=lambda x: x.objectives[feature])

            min_dist = float(front[0].objectives[feature])
            max_dist = float(front[-1].objectives[feature])

            if max_dist == min_dist:
                for i in range(len(front) - 1):
                    front[i].crowding_distance = 0
                front[-1].crowding_distance = float('inf')
            else:
                front[0].crowding_distance = float('inf')
                front[-1].crowding_distance = float('inf')
                for i in range(1, len(front) - 1):
                    front[i].crowding_distance += \
                        (front[i + 1].objectives[feature] - front[i - 1].objectives[feature]) / \
                        (max_dist - min_dist)

    def evaluate_multiple(self, individuals):
        fitness_values = []
        for ind in individuals:
            MultiObjectiveFitness.calculate_objectives(ind, self.target_sound)

        fronts = MultiObjectiveFitness.fast_non_dominated_sort(individuals)
        for rank in fronts:
            MultiObjectiveFitness.calculate_crowding_distances(fronts[rank])
            for ind in fronts[rank]:
                fitness = 1.0 / (rank + (0.5 / (1.0 + ind.crowding_distance)))
                fitness_values.append(fitness)
        return fitness_values


class HybridFitness(AbstractFitness):
    IS_FITNESS_RELATIVE = True

    def __init__(self, target_sound):
        super(HybridFitness, self).__init__(target_sound)
        self.similarity_fitness = LocalSimilarityFitness(target_sound)
        self.multi_objective_fitness = MultiObjectiveFitness(target_sound)

    def evaluate_multiple(self, individuals):
        fitness_values = self.multi_objective_fitness.evaluate_multiple(individuals)
        for i, ind in enumerate(individuals):
            fitness = self.similarity_fitness.get_local_similarity(
                self.target_sound,
                ind.output_sound
            )
            fitness_values[i] = (fitness_values[i] + fitness) / 2
        return fitness_values


class NoveltyFitness(AbstractFitness):
    IS_FITNESS_RELATIVE = True

    def __init__(self, target_sound):
        super(NoveltyFitness, self).__init__(target_sound)
        self.analysis_vectors = []

    @staticmethod
    def get_analysis_vector(ind):
        return np.concatenate(
            tuple(
                ind.output_sound.analysis['series_standardized'][feature]
                for feature in ind.output_sound.analysis['series_standardized']
            ),
            axis=0
        )

    def evaluate_multiple(self, individuals):
        if len(self.analysis_vectors) == 0:
            for ind in individuals:
                analysis_vector = NoveltyFitness.get_analysis_vector(ind)
                self.analysis_vectors.append(analysis_vector)
            return [random.random() for _ in individuals]
        else:
            fitness_values = []
            for ind in individuals:
                distances = []
                analysis_vector = NoveltyFitness.get_analysis_vector(ind)
                for other_analysis_vector in self.analysis_vectors:
                    distance = np.linalg.norm(analysis_vector - other_analysis_vector)
                    distances.append(distance)
                distances.sort()
                k_min_distances = sum(distances[0:3])
                fitness_values.append(k_min_distances)
                self.analysis_vectors.append(analysis_vector)
            max_fitness = max(fitness_values)
            fitness_values = map(lambda x: x / (1.0 + max_fitness), fitness_values)
            return fitness_values
