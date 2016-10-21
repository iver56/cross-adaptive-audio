from __future__ import division
import cross_adapt
import argparse
import experiment
import effect
import sound_file
import random
import math
import settings


"""
Usage example:
$ python try_effect.py -i noise.wav --effect lpf --seed 4
This will produce an output sound where the parameters are controlled by random LFOs
"""

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '-i',
        '--input',
        dest='input_file',
        type=str,
        help='The filename of the input sound',
        required=True
    )
    arg_parser.add_argument(
        '-s',
        '--seed',
        dest='seed',
        help='PRNG seed. Will be set to a random value if not specified.',
        type=int,
        required=False,
        default=42
    )
    arg_parser.add_argument(
        '--effect',
        dest='effect_name',
        type=str,
        help='The name of the sound effect to use. See the effects folder for options.',
        required=False,
        default="dist_lpf"
    )
    args = arg_parser.parse_args()

    input_sound = sound_file.SoundFile(
        args.input_file,
        is_input=True,
        verify_file=True
    )

    experiment_data = {
        'input_sound': input_sound.get_serialized_representation(),
        'args': vars(args)
    }
    experiment.Experiment.calculate_current_experiment_id(experiment_data)

    that_effect = effect.Effect(args.effect_name)
    cross_adapter = cross_adapt.CrossAdapter(
        input_sound=input_sound,
        neural_input_vectors=None,
        effect=that_effect,
        parameter_lpf_cutoff=10
    )

    parameter_vectors = []
    lfo_frequencies = [
        0.1 + 2 * random.random()
        for _ in range(that_effect.num_parameters)
        ]
    lfo_offsets = [
        math.pi * 2 * random.random()
        for _ in range(that_effect.num_parameters)
        ]

    num_frames = int(math.ceil(input_sound.num_samples / settings.HOP_SIZE))
    for i in range(num_frames):
        parameter_vector = [
            0.5 + 0.5 * math.sin(
                lfo_offsets[j] +
                math.pi * 2 * lfo_frequencies[j] * i * settings.HOP_SIZE / settings.SAMPLE_RATE
            )
            for j in range(that_effect.num_parameters)
            ]
        parameter_vectors.append(parameter_vector)

    process, output_sound_file, csd_path = cross_adapter.cross_adapt(
        parameter_vectors=parameter_vectors,
        effect=that_effect,
        output_filename=args.input_file + '.processed.wav'
    )
    process.wait()
    print('folder name: {}'.format(experiment.Experiment.folder_name))
