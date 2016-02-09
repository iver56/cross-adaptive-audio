import statistics


class FitnessEvaluator(object):
    @staticmethod
    def evaluate(sound_file_a, sound_file_c):
        """
        How much does sound_file_c sound like sound_file_a
        :param sound_file_a: SoundFile instance
        :param sound_file_c: SoundFile instance
        :return:
        """
        analysis_a = sound_file_a.get_analysis()
        analysis_c = sound_file_c.get_analysis()

        mean_amp_a = statistics.mean(analysis_a['series']['mfcc_amp'])
        mean_amp_c = statistics.mean(analysis_c['series']['mfcc_amp'])

        mean_amp_difference = abs(mean_amp_c - mean_amp_a)

        return 1.0 / (1 + mean_amp_difference)
