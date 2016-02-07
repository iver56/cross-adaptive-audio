from __future__ import absolute_import
from __future__ import print_function
import sys
import pygame
import argparse
import json
import os
import datetime
import settings
import sound_file
import standardizer
from six.moves import range


class Gfx(object):
    size = width, height = 960, 540
    BLACK = 255, 255, 255

    def __init__(self, series, ksmps=None, input_sound_filename=None):
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        self.fps = 30.0
        self.series = series
        self.num_series = len(self.series)
        self.height_per_series = float(self.height) / self.num_series
        self.num_frames = len(self.series[list(self.series.keys())[0]])
        if settings.VERBOSE:
            print(self.num_series, 'series')
            print(self.num_frames, 'frames')
        self.width_per_frame = float(self.width) / self.num_frames

        self.ksmps = ksmps
        self.sound = None if input_sound_filename is None else pygame.mixer.Sound(input_sound_filename)
        self.t_start = None

    def start_sound(self):
        if self.sound is not None:
            self.sound.play()
        self.t_start = datetime.datetime.now()

    def get_time_since_start(self):
        return (datetime.datetime.now() - self.t_start).total_seconds()

    def draw_series(self):
        i = 0
        for key, array in six.iteritems(self.series):
            for j in range(len(array)):
                normalized_value = standardizer.Standardizer.get_normalized_value(array[j])
                color_value = max(min(int(255 * normalized_value), 255), 0)
                color = (color_value, color_value, color_value)
                rect = pygame.Rect(
                    int(j * self.width_per_frame),
                    int(i * self.height_per_series),
                    self.width_per_frame,
                    self.height_per_series
                )
                pygame.draw.rect(self.screen, color, rect)
            i += 1

    def get_current_frame_number(self):
        return self.get_time_since_start() * float(settings.SAMPLE_RATE) / self.ksmps

    def draw_playhead(self):
        x_position = self.width_per_frame * self.get_current_frame_number()

        color = (220, 80, 80)
        rect = pygame.Rect(
            int(x_position),
            0,
            int(8 * self.width_per_frame),
            self.height
        )
        pygame.draw.rect(self.screen, color, rect)

    def draw(self):
        if self.get_current_frame_number() > self.num_frames:
            sys.exit()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.fps /= 2  # halve the fps
                if event.key == pygame.K_UP:
                    self.fps *= 2  # double the fps
                    if self.fps > 256.0:
                        self.fps = 256.0

        self.clock.tick(self.fps)

        self.screen.fill(self.BLACK)

        self.draw_series()

        if self.ksmps is not None:
            self.draw_playhead()

        if settings.VERBOSE:
            print(self.get_time_since_start())

        pygame.display.flip()


class Visualize(object):
    def __init__(self):
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument(
            '-i',
            '--input_sound_filename',
            dest='input_sound_filename',
            type=str,
            help='The name of the sound file (wav)',
            required=False
        )
        self.args = arg_parser.parse_args()

        self.feature_data = None
        self.gfx = None

        self.read_files()
        self.run()

    def read_files(self):
        input_sound_file = sound_file.SoundFile(self.args.input_sound_filename)
        feature_data_file_path = input_sound_file.get_feature_data_file_path()
        with settings.FILE_HANDLER(feature_data_file_path, 'rb') as data_file:
            self.feature_data = json.load(data_file)

    def run(self):
        self.gfx = Gfx(
            self.feature_data['series_standardized'],
            self.feature_data['ksmps'],
            os.path.join(settings.INPUT_DIRECTORY, self.args.input_sound_filename)
        )
        self.gfx.start_sound()

        for i in range(2000):
            self.gfx.draw()


if __name__ == '__main__':
    pygame.init()
    Visualize()
