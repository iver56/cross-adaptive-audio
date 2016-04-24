from __future__ import print_function
import math
import standardizer
import settings
import analyze


class FitnessEvaluator(object):
    GLOBAL_SIMILARITY_WEIGHT = 1.0
    LOCAL_SIMILARITY_WEIGHT = 1.0

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
                output_value = output_sound.analysis['series_standardized'][feature][k]

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


class CommandLineFitnessTool(object):
    def __init__(self):
        import argparse
        import sound_file
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument(
            '-i',
            '--input',
            dest='input_files',
            nargs='+',
            type=str,
            help='The names of the two sound files to be compared',
            required=True,
            default=[]
        )
        args = arg_parser.parse_args()
        if len(args.input_files) == 2:
            sound_file_a = sound_file.SoundFile(args.input_files[0])
            sound_file_b = sound_file.SoundFile(args.input_files[1])

            analyze.Analyzer.analyze_multiple([sound_file_a, sound_file_b], standardize=True)

            print(FitnessEvaluator.evaluate(sound_file_a, sound_file_b))
        else:
            raise Exception('Two file names must be specified')


if __name__ == '__main__':
    CommandLineFitnessTool()
