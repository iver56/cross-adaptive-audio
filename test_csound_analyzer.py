from __future__ import absolute_import
import unittest
import settings
import sound_file
import time
import csound_analyzer
import experiment


class TestCsoundAnalyzer(unittest.TestCase):
    def setUp(self):
        settings.INPUT_DIRECTORY = 'test_audio'
        self.sounds = [
            sound_file.SoundFile('drums.wav'),
            sound_file.SoundFile('noise.wav')
        ]
        self.csound_analyzer = csound_analyzer.CsoundAnalyzer(['csound_rms'])
        experiment.Experiment.folder_name = 'test'

    def test_analysis(self):
        self.start_time = time.time()

        self.csound_analyzer.analyze_multiple(self.sounds)

        for sound in self.sounds:
            self.assertTrue('csound_rms' in sound.analysis['series'])
            self.assertGreater(len(sound.analysis['series']['csound_rms']), 100)

        print("Execution time: {0} seconds".format(
            time.time() - self.start_time)
        )

    def test_unpack_numbers(self):
        numbers = tuple(range(16))
        unpacked_numbers = csound_analyzer.CsoundAnalyzer.unpack_numbers(numbers, num_series=4)
        self.assertEqual(
            unpacked_numbers,
            [
                (0, 4, 8, 12),
                (1, 5, 9, 13),
                (2, 6, 10, 14),
                (3, 7, 11, 15)
            ]
        )


if __name__ == '__main__':
    unittest.main()
