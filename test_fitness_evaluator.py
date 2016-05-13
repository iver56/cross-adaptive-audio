import unittest
import settings
import sound_file
import fitness_evaluator
import project
import individual


class TestFitnessEvaluator(unittest.TestCase):
    def setUp(self):
        settings.INPUT_DIRECTORY = 'test_audio'

    def test_fitness_evaluator(self):
        drums = sound_file.SoundFile('drums.wav')
        synth = sound_file.SoundFile('synth.wav')

        ind1 = individual.Individual(
            genotype=None,
            neural_input_mode=None,
            effect=None
        )
        ind1.set_output_sound(drums)
        ind2 = individual.Individual(
            genotype=None,
            neural_input_mode=None,
            effect=None
        )
        ind2.set_output_sound(synth)

        # make sure sound files are analyzed
        project.Project([ind1.output_sound, ind2.output_sound])

        # mock
        ind1.set_fitness = lambda x: None
        ind2.set_fitness = lambda x: None

        fitness_evaluator.FitnessEvaluator.evaluate_multiple([ind1, ind2], drums)

if __name__ == '__main__':
    unittest.main()
