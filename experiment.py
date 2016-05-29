import json
import hashlib
import time
import os
import settings


class Experiment(object):
    current_experiment_id = None
    start_time = None
    folder_name = './'
    experiment_settings = None
    SIMILARITY_CHANNELS = None
    SIMILARITY_WEIGHTS = None
    NEURAL_INPUT_CHANNELS = None
    PARAMETER_LPF_CUTOFF = None

    @staticmethod
    def load_experiment_settings(filename):
        with open(os.path.join('experiment_settings', filename), 'r') as data_file:
            Experiment.experiment_settings = json.load(data_file)
            Experiment.SIMILARITY_CHANNELS = []
            Experiment.SIMILARITY_WEIGHTS = {}

            for similarity_feature in Experiment.experiment_settings['similarity_channels']:
                if isinstance(similarity_feature, dict) and 'name' in similarity_feature:
                    feature = str(similarity_feature['name'])
                    weight = similarity_feature.get('weight', 1.0)
                    if weight <= 0.0:
                        print(
                            'Warning: Ignoring feature {0} with weight {1}'
                            ' (only positive similarity weights are supported)'.format(
                                feature,
                                weight
                            )
                        )
                        continue
                    Experiment.SIMILARITY_CHANNELS.append(feature)
                    Experiment.SIMILARITY_WEIGHTS[feature] = weight
                elif isinstance(similarity_feature, str) or isinstance(similarity_feature, unicode):
                    feature = str(similarity_feature)
                    Experiment.SIMILARITY_CHANNELS.append(feature)
                    Experiment.SIMILARITY_WEIGHTS[feature] = 1.0
                else:
                    print(
                        'Warning: Could not parse similarity channel {0} in file {1}'.format(
                            similarity_feature,
                            filename
                        )
                    )
            if len(Experiment.SIMILARITY_CHANNELS) == 0:
                raise Exception('No valid similarity features specified')
            Experiment.NEURAL_INPUT_CHANNELS = Experiment.experiment_settings['neural_input_channels']
            Experiment.PARAMETER_LPF_CUTOFF = Experiment.experiment_settings['parameter_lpf_cutoff']

    @staticmethod
    def calculate_current_experiment_id(experiment_representation):
        Experiment.current_experiment_id = hashlib.md5(
            json.dumps(experiment_representation).encode('utf-8')
        ).hexdigest()
        Experiment.start_time = time.strftime("%Y%m%dT%H%M%S", time.gmtime())  # ISO 8601
        Experiment.folder_name = Experiment.start_time + '__' + Experiment.current_experiment_id[0:8]

        Experiment.ensure_folders()

    @staticmethod
    def ensure_folders():
        folders = [
            settings.CSD_DIRECTORY,
            settings.INDIVIDUAL_DATA_DIRECTORY,
            settings.OUTPUT_DIRECTORY,
            settings.STATS_DATA_DIRECTORY,
            settings.TEMP_DIRECTORY
        ]
        for folder in folders:
            experiment_subfolder = os.path.join(folder, Experiment.folder_name)
            if not os.path.exists(experiment_subfolder):
                os.makedirs(experiment_subfolder)
