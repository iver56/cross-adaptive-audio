import json


with open('experiment_settings.json') as data_file:
    experiment_settings = json.load(data_file)
    SIMILARITY_CHANNELS = experiment_settings['similarity_channels']
    NEURAL_INPUT_CHANNELS = experiment_settings['neural_input_channels']
    PARAMETER_LPF_CUTOFF = experiment_settings['parameter_lpf_cutoff']
