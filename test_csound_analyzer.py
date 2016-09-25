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
            sound_file.SoundFile('vocal.wav')
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


if __name__ == '__main__':
    unittest.main()
