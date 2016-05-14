import json


with open('experiment_settings.json', 'r') as data_file:
    experiment_settings = json.load(data_file)
    SIMILARITY_CHANNELS = []
    SIMILARITY_WEIGHTS = {}

    for similarity_feature in experiment_settings['similarity_channels']:
        if isinstance(similarity_feature, dict) and 'name' in similarity_feature:
            feature = str(similarity_feature['name'])
            weight = similarity_feature.get('weight', 1.0)
            if weight <= 0.0:
                print(
                    'Warning: Ignoring feature {0} with weight {1}'
                    ' (only positive similarity weights are supported)'.format(feature, weight)
                )
                continue
            SIMILARITY_CHANNELS.append(feature)
            SIMILARITY_WEIGHTS[feature] = weight
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
    if len(SIMILARITY_CHANNELS) == 0:
        raise Exception('No valid similarity features specified')
    NEURAL_INPUT_CHANNELS = experiment_settings['neural_input_channels']
    PARAMETER_LPF_CUTOFF = experiment_settings['parameter_lpf_cutoff']
