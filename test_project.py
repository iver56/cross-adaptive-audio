from __future__ import absolute_import
import unittest
import settings
import project


class TestProject(unittest.TestCase):
    def setUp(self):
        settings.CURRENT_PROJECT_FILE = 'test.json'

    def test_project(self):
        my_project = project.Project.get_current_project()
        print(my_project.data)

if __name__ == '__main__':
    unittest.main()
