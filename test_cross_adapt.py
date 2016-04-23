from __future__ import absolute_import
import unittest
import settings
import os
import sound_file
import cross_adapt
import time
import project


class TestCrossAdapt(unittest.TestCase):
    def setUp(self):
        settings.INPUT_DIRECTORY = 'test_audio'
        project.Project.assert_project_exists()

    def test_sound_file(self):
        target_sound = sound_file.SoundFile('drums.wav')
        input_sound = sound_file.SoundFile('noise.wav')
        num_frames = min(
            target_sound.get_num_frames(),
            input_sound.get_num_frames()
        )
        print('num_frames', num_frames)
        constant_parameter_vector = [0.5] * cross_adapt.CrossAdapter.NUM_PARAMETERS
        parameter_vectors = [constant_parameter_vector] * num_frames

        self.start_time = time.time()

        output_sound_file, that_neural_output = cross_adapt.CrossAdapter.cross_adapt(
            target_sound,
            input_sound,
            parameter_vectors,
            generation=0
        )

        print("Execution time: {0} seconds".format(
            time.time() - self.start_time)
        )


if __name__ == '__main__':
    unittest.main()
