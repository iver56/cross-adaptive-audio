from __future__ import absolute_import
import unittest
import settings
import sound_file


class TestSoundFile(unittest.TestCase):
    def setUp(self):
        settings.INPUT_DIRECTORY = 'test_audio'

    def test_sound_file(self):
        my_sound_file = sound_file.SoundFile('drums.wav')
        self.assertEqual(my_sound_file.get_md5(), 'f1a64ffcd2c2c3d7b5fa27cfb520c626')
        self.assertAlmostEqual(my_sound_file.get_duration(), 7.89278911565)

if __name__ == '__main__':
    unittest.main()
