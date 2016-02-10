from __future__ import print_function
import math
import standardizer
import settings


class FitnessEvaluator(object):
    @staticmethod
    def evaluate(param_sound, output_sound):
        """
        How much does sound_file_c sound like sound_file_a
        :param param_sound: SoundFile instance
        :param output_sound: SoundFile instance
        :return:
        """

        # Compare global stats:
        param_standardizer = standardizer.Standardizer([param_sound])
        output_standardizer = standardizer.Standardizer([output_sound])
        param_sound_stats = param_standardizer.calculate_feature_statistics(series_key='series_standardized')
        output_sound_stats = output_standardizer.calculate_feature_statistics(series_key='series_standardized')

        global_param_feature_vector = []
        for feature_stats in param_sound_stats:
            for stat in param_sound_stats[feature_stats]:
                global_param_feature_vector.append(param_sound_stats[feature_stats][stat])

        global_output_feature_vector = []
        for feature_stats in output_sound_stats:
            for stat in output_sound_stats[feature_stats]:
                global_output_feature_vector.append(output_sound_stats[feature_stats][stat])

        global_stats_distance = FitnessEvaluator.get_euclidean_distance(
            global_output_feature_vector,
            global_param_feature_vector
        )

        if settings.VERBOSE:
            print('global_stats_distance', global_stats_distance)

        fitness = 1.0 / (1 + global_stats_distance)
        return fitness

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
            print(FitnessEvaluator.evaluate(sound_file_a, sound_file_b))
        else:
            raise Exception('Two file names must be specified')

if __name__ == '__main__':
    CommandLineFitnessTool()
