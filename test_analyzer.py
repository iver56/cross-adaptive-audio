from __future__ import absolute_import
import unittest
import settings
import sound_file
import time
from analyze import Analyzer


class TestAnalyzer(unittest.TestCase):
    def setUp(self):
        settings.INPUT_DIRECTORY = 'test_audio'
        self.sounds = [
            sound_file.SoundFile('drums.wav'),
            sound_file.SoundFile('noise.wav'),
            sound_file.SoundFile('synth.wav'),
            sound_file.SoundFile('vocal.wav')
        ]
        self.analyzer = Analyzer(project=None)

    def test_serial_analysis(self):
        self.start_time = time.time()

        for sound in self.sounds:
            self.analyzer.analyze_multiple([sound], standardize=False)

        print("Serial execution time: {0} seconds".format(
            time.time() - self.start_time)
        )

    def test_parallel_analysis(self):
        self.start_time = time.time()

        self.analyzer.analyze_multiple(self.sounds, standardize=False)

        print("Parallel execution time: {0} seconds".format(
            time.time() - self.start_time)
        )


if __name__ == '__main__':
    unittest.main()
