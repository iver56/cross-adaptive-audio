import settings
import template_handler
import os
import csound_handler
import sound_file
import argparse
import numpy as np


class DataAugmenter(object):
    def __init__(self):
        self.template_dir = settings.EFFECT_DIRECTORY
        template_file_path = os.path.join(settings.EFFECT_DIRECTORY, 'data_augmentation.csd.jinja2')
        with open(template_file_path, 'r') as template_file:
            self.template_string = template_file.read()

        self.template_handler = template_handler.TemplateHandler(
            template_dir=self.template_dir,
            template_string=self.template_string
        )

    def augment(self, sound, factor, pause_between, seed, keep_csd=False):
        assert factor >= 2
        if seed >= 0:
            np.random.seed(seed)

        start_time = 0.001
        playback_speed_values = np.clip(
            np.exp(np.random.normal(0, 0.3, factor)),
            0.66,
            1.5
        )
        gain_values = np.clip(
            np.exp(np.random.normal(0, 0.5, factor)),
            0.05,
            3
        )
        playback_speed_values[0] = 1.0
        gain_values[0] = 1.0
        events = []
        for i in range(factor):
            playback_speed = playback_speed_values[i]
            gain = gain_values[i]
            duration = sound.get_duration() / playback_speed
            events.append({
                'start': start_time,
                'duration': duration,
                'playback_speed': playback_speed,
                'gain': gain
            })
            start_time += duration + pause_between

        self.template_handler.compile(
            input_sound=sound,
            ksmps=settings.HOP_SIZE,
            factor=factor,
            events=events
        )
        csd_path = os.path.join(
            settings.TEMP_DIRECTORY,
            'data_augmentation.csd'
        )
        self.template_handler.write_result(csd_path)

        csound = csound_handler.CsoundHandler(csd_path)

        output_file_path = os.path.join(
            settings.INPUT_DIRECTORY,
            sound.filename + '.augmented.wav'
        )
        csound.run(
            input_file_path=None,
            output_file_path=output_file_path,
            async=False
        )
        if not keep_csd:
            os.remove(csd_path)

        return output_file_path


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        '-i',
        '--input',
        type=str,
        dest='input',
        help='Which input sound file to augment (this file should reside in the input folder)',
        required=True
    )
    arg_parser.add_argument(
        '--factor',
        dest='factor',
        type=int,
        required=False,
        default=4
    )
    arg_parser.add_argument(
        '--pause-between',
        dest='pause_between',
        type=float,
        required=False,
        default=0.05
    )
    arg_parser.add_argument(
        '--keep-csd',
        nargs='?',
        dest='keep_csd',
        help='Keep the csd file that was created to generate the extended sound',
        const=True,
        required=False,
        default=False
    )
    arg_parser.add_argument(
        '--seed',
        dest='seed',
        type=int,
        required=False,
        default=-1
    )
    args = arg_parser.parse_args()

    that_sound = sound_file.SoundFile(args.input, verify_file=True)
    that_output_file_path = DataAugmenter().augment(
        that_sound,
        factor=args.factor,
        pause_between=args.pause_between,
        seed=args.seed,
        keep_csd=args.keep_csd
    )
    print('Successfully created augmented sound: {}'.format(that_output_file_path))
