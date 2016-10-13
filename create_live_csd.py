from __future__ import absolute_import
from __future__ import print_function
import settings
import os
import argparse
import json
import template_handler
import effect


def resolve_paths(individual_id):
    experiment_folder_name = None
    individual_data_file_paths = []
    for root, dirs, filenames in os.walk(settings.INDIVIDUAL_DATA_DIRECTORY):
        for filename in filenames:
            if individual_id in filename and filename.endswith('.json'):
                experiment_folder_name = root.split('\\')[-1]
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
    args = arg_parser.parse_args()

    experiment_folder_name, stats_file_path, individual_data_file_path = resolve_paths(args.individual_id)

    print('stats_file_path', stats_file_path)
    with open(stats_file_path, 'r') as data_file:
        project_data = json.load(data_file)

    print('individual data file path', individual_data_file_path)

    that_effect = effect.Effect.get_effect_by_name(project_data['args']['effect_name'])

    features = project_data['experiment_settings']['neural_input_channels']
    if len(features) != 2 or 'csound_rms' not in features or 'csound_spectral_centroid' not in features:
        raise Exception('Parameters must be 2 parameters analyzed by csound analyzer (this is a proof of concept for now)')

    template = template_handler.TemplateHandler(
        that_effect.template_file_path,
        transform_template_string=lambda template_string: template_string.replace(
            'base_template.csd.jinja2',
            'base_template_live.csd.jinja2'
        )
    )
    template.compile(
        parameter_names=that_effect.parameter_names,
        ksmps=settings.HOP_SIZE,
        duration=args.duration,
        parameter_lpf_cutoff=project_data['experiment_settings']['parameter_lpf_cutoff'],
        individual_id=args.individual_id
    )

    csd_path = os.path.join(
        settings.CSD_DIRECTORY,
        experiment_folder_name,
        args.individual_id + '.live.csd'
    )
    template.write_result(csd_path)


if __name__ == '__main__':
    create_live_csd()
