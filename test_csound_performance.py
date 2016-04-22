from __future__ import absolute_import
import unittest
import settings
import sound_file
import template_handler
import csound_handler
import os
import time


class TestCsoundPerformance(unittest.TestCase):
    def setUp(self):
        settings.INPUT_DIRECTORY = 'test_audio'
        self.num_sounds = 20
        self.drums = sound_file.SoundFile('drums.wav')
        self.files_to_delete = []

    def tearDown(self):
        for file_path in self.files_to_delete:
            os.remove(file_path)

    def test_serial_execution(self):
        self.start_time = time.time()

        for i in range(self.num_sounds):
            template = template_handler.TemplateHandler('templates/test_effect.csd.jinja2')
            duration = self.drums.get_duration()
            template.compile(
                sound_filename=self.drums.filename,
                ksmps=settings.CSOUND_KSMPS,
                duration=duration
            )

            csd_path = os.path.join(settings.CSD_DIRECTORY, 'test_effect_{}.csd'.format(i))
            template.write_result(csd_path)
            csound = csound_handler.CsoundHandler(csd_path)
            output_filename = self.drums.filename + '.test_processed_{}.wav'.format(i)
            csound.run(output_filename, async=False)
            self.files_to_delete.append(csd_path)
            self.files_to_delete.append(os.path.join(settings.OUTPUT_DIRECTORY, output_filename))

        print("Serial execution time for {0} sounds: {1} seconds".format(
            self.num_sounds,
            time.time() - self.start_time)
        )

    def test_parallel_execution(self):
        self.start_time = time.time()

        processes = []

        for i in range(self.num_sounds):
            template = template_handler.TemplateHandler('templates/test_effect.csd.jinja2')
            duration = self.drums.get_duration()
            template.compile(
                sound_filename=self.drums.filename,
                ksmps=settings.CSOUND_KSMPS,
                duration=duration
            )

            csd_path = os.path.join(settings.CSD_DIRECTORY, 'test_effect_{}.csd'.format(i))
            template.write_result(csd_path)
            csound = csound_handler.CsoundHandler(csd_path)
            output_filename = self.drums.filename + '.test_processed_{}.wav'.format(i)
            p = csound.run(output_filename, async=True)
            processes.append(p)
            self.files_to_delete.append(csd_path)
            self.files_to_delete.append(os.path.join(settings.OUTPUT_DIRECTORY, output_filename))

        for p in processes:
            p.wait()

        print("Parallel execution time for {0} sounds: {1} seconds".format(
            self.num_sounds,
            time.time() - self.start_time)
        )


if __name__ == '__main__':
    unittest.main()
