from __future__ import absolute_import
import unittest
import settings
import sound_file
import cross_adapt
import time
import project
import effect
import copy
import analyze


class TestCrossAdapt(unittest.TestCase):
    def setUp(self):
        settings.INPUT_DIRECTORY = 'test_audio'
        project.Project.assert_project_exists()

    def test_sound_file(self):
        that_effect = effect.effects['dist_lpf']
        target_sound = sound_file.SoundFile('drums.wav')
        input_sound = sound_file.SoundFile('noise.wav')

        analyze.Analyzer.analyze_multiple([target_sound, input_sound], standardize=True)

        num_frames = min(
            target_sound.get_num_frames(),
            input_sound.get_num_frames()
        )
        print('num_frames', num_frames)
        constant_parameter_vector = [0.5] * that_effect.num_parameters
        parameter_vectors = [copy.deepcopy(constant_parameter_vector) for i in range(num_frames)]

        self.start_time = time.time()

        output_sound_file = cross_adapt.CrossAdapter.cross_adapt(
            input_sound,
            parameter_vectors,
            that_effect,
            generation=0
        )

        print("Execution time: {0} seconds".format(
            time.time() - self.start_time)
        )


if __name__ == '__main__':
    unittest.main()
