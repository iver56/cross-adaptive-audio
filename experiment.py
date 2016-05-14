import json


with open('experiment_settings.json', 'r') as data_file:
    experiment_settings = json.load(data_file)
    SIMILARITY_CHANNELS = []
    SIMILARITY_WEIGHTS = {}

    for similarity_feature in experiment_settings['similarity_channels']:
        if isinstance(similarity_feature, dict) and 'name' in similarity_feature:
            feature = str(similarity_feature['name'])
            SIMILARITY_CHANNELS.append(feature)
            SIMILARITY_WEIGHTS[feature] = similarity_feature.get('weight', 1.0)
        elif isinstance(similarity_feature, str) or isinstance(similarity_feature, unicode):
            feature = str(similarity_feature)
            SIMILARITY_CHANNELS.append(feature)
            SIMILARITY_WEIGHTS[feature] = 1.0
        else:
            print(
                'Warning: Could not parse similarity channel {} in experiment_settings.json'.format(
                    similarity_feature
                )
            )
    NEURAL_INPUT_CHANNELS = experiment_settings['neural_input_channels']
    PARAMETER_LPF_CUTOFF = experiment_settings['parameter_lpf_cutoff']
