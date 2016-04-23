from __future__ import absolute_import
import unittest
import settings
import sound_file
import time
from analyze import Analyzer


class TestCrossAdapt(unittest.TestCase):
    def setUp(self):
        settings.INPUT_DIRECTORY = 'test_audio'
        self.sounds = [
            sound_file.SoundFile('drums.wav'),
            sound_file.SoundFile('noise.wav'),
            sound_file.SoundFile('synth.wav'),
            sound_file.SoundFile('vocal.wav')
        ]

    def test_serial_analysis(self):
        self.start_time = time.time()

        for sound in self.sounds:
            Analyzer.analyze_mfcc(sound)

        print("Serial execution time: {0} seconds".format(
            time.time() - self.start_time)
        )

    def test_multithreading(self):
        from multiprocessing.dummy import Pool  # thread pool
        from subprocess import Popen, PIPE, STDOUT

        self.start_time = time.time()

        commands = [Analyzer.get_analyze_mfcc_command(sound) for sound in self.sounds]

        # run commands in parallel
        processes = [
            Popen(
                command,
                stdin=PIPE,
                stdout=PIPE,
                stderr=STDOUT
            )
            for command in commands
            ]

        # collect output in parallel
        def get_lines(process):
            return process.communicate()[0].splitlines()

        outputs = Pool(len(processes)).map(get_lines, processes)

        print("Parallel execution time: {0} seconds".format(
            time.time() - self.start_time)
        )


if __name__ == '__main__':
    unittest.main()
