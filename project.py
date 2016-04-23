from __future__ import absolute_import
import json
import os
import settings


class Project(object):
    current_project = None

    def __init__(self, filename):
        self.filename = filename

        self.data = None
        self.fetch_project_data()

    def fetch_project_data(self):
        project_data_file_path = os.path.join(settings.PROJECT_DATA_DIRECTORY, self.filename)
        if os.path.isfile(project_data_file_path):
            with settings.FILE_HANDLER(project_data_file_path) as project_data_file_path:
                self.data = json.load(project_data_file_path)

    @staticmethod
    def assert_project_exists():
        if Project.get_current_project().data is None:
            raise Exception(
                'Could not find project "{}".'
                ' You can create a project by running `make project`'.format(
                    settings.CURRENT_PROJECT_FILE
                )
            )

    @staticmethod
    def get_current_project():
        if Project.current_project is None:
            Project.current_project = Project(settings.CURRENT_PROJECT_FILE)
        return Project.current_project
