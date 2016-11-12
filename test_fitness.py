import unittest
import settings
import sound_file
import fitness
import project
import individual
import experiment
import analyze


class TestFitness(unittest.TestCase):
    def setUp(self):
        settings.INPUT_DIRECTORY = 'test_audio'
        experiment.Experiment.load_experiment_settings('mfcc_basic.json')
        analyze.Analyzer.init_features_list()

    def test_fitness(self):
        drums = sound_file.SoundFile('drums.wav')
        synth = sound_file.SoundFile('synth.wav')

        ind1 = individual.Individual(
            genotype=None,
            neural_mode=None,
            effect=None
        )
        ind1.set_output_sound(drums)
        ind2 = individual.Individual(
            genotype=None,
            neural_mode=None,
            effect=None
        )
        ind2.set_output_sound(synth)

        # make sure sound files are analyzed
        project.Project([ind1.output_sound, ind2.output_sound])

        # mock
        ind1.set_fitness = lambda x: None
        ind2.set_fitness = lambda x: None

        fitness_evaluator = fitness.LocalSimilarityFitness(target_sound=drums)
        fitness_evaluator.evaluate_multiple([ind1, ind2])

if __name__ == '__main__':
    unittest.main()
