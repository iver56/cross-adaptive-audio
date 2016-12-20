from __future__ import absolute_import
from __future__ import print_function
import settings
import os
import argparse
import json
import template_handler
import effect
import sys
import base64


def resolve_paths(individual_id):
    experiment_folder_name = None
    individual_data_file_paths = []
    for root, dirs, filenames in os.walk(settings.INDIVIDUAL_DATA_DIRECTORY):
        for filename in filenames:
            if individual_id in filename and filename.endswith('.json'):
                experiment_folder_name = os.path.basename(os.path.normpath(root))
                path = os.path.join(root, filename)
                individual_data_file_paths.append(path)
    if len(individual_data_file_paths) > 1:
        raise Exception('There are multiple individuals with that individual id')
    elif len(individual_data_file_paths) == 0:
        raise Exception('Could not find that individual')

    stats_file_path = os.path.join(
        settings.STATS_DATA_DIRECTORY,
        experiment_folder_name,
        'stats.json'
    )
    return experiment_folder_name, stats_file_path, individual_data_file_paths[0]


def create_live_csd():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '-i',
        '--id',
        dest='individual_id',
        type=str,
        help='Individual id (or a unique part of it)',
        required=True
    )
    arg_parser.add_argument(
        '--duration',
        dest='duration',
        type=float,
        help='Amount of time the csd file should stay alive when executed',
        required=False,
        default=8.0
    )
    # TODO: add ksmps argument
    # TODO: add argument for which input sounds to use
    # TODO: include all necessary python code inside the csd file
    args = arg_parser.parse_args()

    experiment_folder_name, stats_file_path, individual_data_file_path = resolve_paths(args.individual_id)

    # print('stats_file_path', stats_file_path)
    with open(stats_file_path, 'r') as data_file:
        project_data = json.load(data_file)

    # print('individual data file path', individual_data_file_path)

    with open(individual_data_file_path, 'r') as data_file:
        individual_data = json.load(data_file)

    parameter_data = {
        'feature_statistics': project_data['feature_statistics'],
        'experiment_settings': {
            'neural_input_channels': project_data['experiment_settings']['neural_input_channels']
        },
        'genotype_pickled': individual_data['genotype_pickled'],
        'args': {
            'effect_names': project_data['args']['effect_names']
        }
    }
    parameter_data_json = json.dumps(parameter_data)
    parameter_data_base64 = base64.b64encode(parameter_data_json)

    if len(project_data['args']['effect_names']) > 1:
        raise Exception('CompositeEffect is not compatible with live mode as of v0.6')

    that_effect = effect.get_effect_instance(project_data['args']['effect_names'])

    features = project_data['experiment_settings']['neural_input_channels']
    if len(features) != 2 or 'csound_rms' not in features or 'csound_spectral_centroid' not in features:
        raise Exception('Parameters must be 2 parameters analyzed by csound analyzer (this is a proof of concept for now)')

    template = that_effect.get_template_handler(live=True)

    template.compile(
        parameter_names=that_effect.parameter_names,
        ksmps=settings.HOP_SIZE,
        duration=args.duration,
        parameter_lpf_cutoff=project_data['experiment_settings']['parameter_lpf_cutoff'],
        parameter_data_base64=parameter_data_base64,
        sys_paths=sys.path
    )

    csd_path = os.path.join(
        settings.LIVE_CSD_DIRECTORY,
        args.individual_id + '.live.csd'
    )
    template.write_result(csd_path)


if __name__ == '__main__':
    create_live_csd()
