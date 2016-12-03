from __future__ import absolute_import
import unittest
import settings
import sound_file
import time
import sonic_annotator_analyzer


class TestSonicAnnotatorAnalyzer(unittest.TestCase):
    def setUp(self):
        settings.INPUT_DIRECTORY = 'test_audio'
        self.sounds = [
            sound_file.SoundFile('drums.wav'),
            sound_file.SoundFile('noise.wav')
        ]
        self.vamp_analyzer = sonic_annotator_analyzer.SonicAnnotatorAnalyzer(['spectral_centroid'])

    def test_analysis(self):
        self.start_time = time.time()

        self.vamp_analyzer.analyze_multiple(self.sounds)

        for sound in self.sounds:
            self.assertTrue('spectral_centroid' in sound.analysis['series'])
            self.assertGreater(len(sound.analysis['series']['spectral_centroid']), 0)

        print("Execution time: {0} seconds".format(
            time.time() - self.start_time)
        )


if __name__ == '__main__':
    unittest.main()
