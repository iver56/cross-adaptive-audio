from __future__ import absolute_import
import unittest
import settings
import sound_file
import project
import experiment


class TestSoundFile(unittest.TestCase):
    def setUp(self):
        settings.INPUT_DIRECTORY = 'test_audio'

    def test_sound_file(self):
        my_sound_file = sound_file.SoundFile('drums.wav')
        self.assertAlmostEqual(my_sound_file.get_duration(), 7.89278911565)

        project.Project([my_sound_file])

        feature_vector_0 = my_sound_file.get_standardized_neural_input_vector(0)
        self.assertEqual(len(feature_vector_0), len(experiment.NEURAL_INPUT_CHANNELS))
        feature_vector_1 = my_sound_file.get_standardized_neural_input_vector(1)
        self.assertNotEqual(feature_vector_0, feature_vector_1)

if __name__ == '__main__':
    unittest.main()
