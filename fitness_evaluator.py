from __future__ import print_function
import math
import standardizer
import settings


class FitnessEvaluator(object):
    GLOBAL_SIMILARITY_WEIGHT = 1.0
    LOCAL_SIMILARITY_WEIGHT = 1.0

    # fitness is not relative, i.e. it doesn't change from generation to generation and doesn't
    # depend on the fitness of other individuals
    IS_FITNESS_RELATIVE = False

    @staticmethod
    def evaluate_multiple(individuals, target_sound):
        for ind in individuals:
            fitness = FitnessEvaluator.evaluate(target_sound, ind.output_sound)
            ind.set_fitness(fitness)

    @staticmethod
    def evaluate(param_sound, output_sound):
        """
        How much does sound_file_c sound like sound_file_a
        :param param_sound: SoundFile instance
        :param output_sound: SoundFile instance
        :return:
        """

        # global_similarity = FitnessEvaluator.get_global_similarity(param_sound, output_sound)
        local_similarity = FitnessEvaluator.get_local_similarity(param_sound, output_sound)

        return (
            # FitnessEvaluator.GLOBAL_SIMILARITY_WEIGHT * global_similarity +
            FitnessEvaluator.LOCAL_SIMILARITY_WEIGHT * local_similarity
        )

    @staticmethod
    def get_global_similarity(param_sound, output_sound):
        # Compare global stats:
        param_standardizer = standardizer.Standardizer([param_sound])
        output_standardizer = standardizer.Standardizer([output_sound])
        param_sound_stats = param_standardizer.calculate_feature_statistics(
            series_key='series_standardized'
        )
        output_sound_stats = output_standardizer.calculate_feature_statistics(
            series_key='series_standardized'
        )

        global_param_feature_vector = []
        for feature_stats in settings.SIMILARITY_CHANNELS:
            for stat in param_sound_stats[feature_stats]:
                global_param_feature_vector.append(param_sound_stats[feature_stats][stat])

        global_output_feature_vector = []
        for feature_stats in settings.SIMILARITY_CHANNELS:
            for stat in output_sound_stats[feature_stats]:
                global_output_feature_vector.append(output_sound_stats[feature_stats][stat])

        global_stats_distance = FitnessEvaluator.get_euclidean_distance(
            global_output_feature_vector,
            global_param_feature_vector
        )

        if settings.VERBOSE:
            print('global_stats_distance', global_stats_distance)

        return 1.0 / (1.0 + global_stats_distance)

    @staticmethod
    def get_local_similarity(param_sound, output_sound):
        euclidean_distance_sum = 0
        for k in range(param_sound.get_num_frames()):
            sum_of_squared_differences = 0
            for feature in settings.SIMILARITY_CHANNELS:
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

                sum_of_squared_differences += (param_value - output_value) ** 2
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


class MultiObjectiveFitnessEvaluator(object):
    # Fitness is relative, i.e. it depends on the fitness of other individuals and may
    # change from generation to generation
    IS_FITNESS_RELATIVE = True

    @staticmethod
    def calculate_objectives(that_individual, target_sound):
        that_individual.objectives = {}
        for feature in settings.SIMILARITY_CHANNELS:
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
                if MultiObjectiveFitnessEvaluator.individual_dominates(p, q):
                    p.individuals_dominated.add(q)
                elif MultiObjectiveFitnessEvaluator.individual_dominates(q, p):
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

        for feature in settings.SIMILARITY_CHANNELS:
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

    @staticmethod
    def evaluate_multiple(individuals, target_sound):
        for ind in individuals:
            MultiObjectiveFitnessEvaluator.calculate_objectives(ind, target_sound)

        fronts = MultiObjectiveFitnessEvaluator.fast_non_dominated_sort(individuals)
        for rank in fronts:
            MultiObjectiveFitnessEvaluator.calculate_crowding_distances(fronts[rank])
            for ind in fronts[rank]:
                fitness = 1.0 / (rank + (0.5 / (1.0 + ind.crowding_distance)))
                ind.set_fitness(fitness)


class HybridFitnessEvaluator(object):
    # Fitness is relative, i.e. it depends on the fitness of other individuals and may
    # change from generation to generation
    IS_FITNESS_RELATIVE = True

    @staticmethod
    def evaluate_multiple(individuals, target_sound):
        MultiObjectiveFitnessEvaluator.evaluate_multiple(individuals, target_sound)
        for ind in individuals:
            fitness = FitnessEvaluator.evaluate(target_sound, ind.output_sound)
            ind.set_fitness(
                (ind.genotype.GetFitness() + fitness) / 2
            )
