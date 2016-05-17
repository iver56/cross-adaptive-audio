from __future__ import absolute_import
import unittest
import settings
import sound_file
import time
import essentia_analyzer
import experiment


class TestEssentiaAnalyzer(unittest.TestCase):
    def setUp(self):
        settings.INPUT_DIRECTORY = 'test_audio'
        self.sounds = [
            sound_file.SoundFile('drums.wav'),
            sound_file.SoundFile('vocal.wav')
        ]
        self.essentia_analyzer = essentia_analyzer.EssentiaAnalyzer(['spectral_centroid'])
        experiment.Experiment.folder_name = 'test'

    def test_analysis(self):
        self.start_time = time.time()

        self.essentia_analyzer.analyze_multiple(self.sounds)

        for sound in self.sounds:
            self.assertTrue('spectral_centroid' in sound.analysis['series'])

        print("Execution time: {0} seconds".format(
            time.time() - self.start_time)
        )


if __name__ == '__main__':
    unittest.main()
