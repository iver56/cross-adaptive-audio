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

        cross_adapter = cross_adapt.CrossAdapter(
            input_sound=input_sound,
            neural_input_vectors=[],
            effect=that_effect
        )

        output_filename = 'test_cross_adapt.wav'

        process, output_sound_file, csd_path = cross_adapter.cross_adapt(
            parameter_vectors,
            that_effect,
            output_filename
        )

        print('process', process)
        print('output file', output_sound_file)
        print('csd path', csd_path)

        process.wait()

        print("Execution time: {0} seconds".format(
            time.time() - self.start_time)
        )


if __name__ == '__main__':
    unittest.main()
