import sys
import pygame
import argparse
import json
import os
import datetime


class Gfx(object):
    size = width, height = 960, 540
    BLACK = 255, 255, 255

    def __init__(self, series, krate=None, sound_filename=None):
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        self.fps = 30.0
        self.series = series
        self.num_series = len(self.series)
        print self.num_series, 'series'
        self.height_per_series = float(self.height) / self.num_series
        self.num_frames = len(self.series[self.series.keys()[0]])
        print self.num_frames, 'frames'
        self.width_per_frame = float(self.width) / self.num_frames

        self.krate = krate
        self.sound = None if sound_filename is None else pygame.mixer.Sound(sound_filename)
        self.t_start = None

    def start_sound(self):
        if self.sound is not None:
            self.sound.play()
        self.t_start = datetime.datetime.now()

    def get_time_since_start(self):
        return (datetime.datetime.now() - self.t_start).total_seconds()

    def draw_series(self):
        i = 0
        for key, array in self.series.iteritems():
            for j in range(len(array)):
                color_value = int(255 * array[j])
                color = (color_value, color_value, color_value)
                rect = pygame.Rect(
                    int(j * self.width_per_frame),
                    int(i * self.height_per_series),
                    self.width_per_frame,
                    self.height_per_series
                )
                pygame.draw.rect(self.screen, color, rect)
            i += 1

    def draw_playhead(self):
        current_frame_number = self.get_time_since_start() * self.krate
        x_position = self.width_per_frame * current_frame_number

        color = (220, 80, 80)
        rect = pygame.Rect(
            int(x_position),
            0,
            int(8 * self.width_per_frame),
            self.height
        )
        pygame.draw.rect(self.screen, color, rect)

    def draw(self):
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

        if self.krate is not None:
            self.draw_playhead()

        print self.get_time_since_start()

        pygame.display.flip()


class Visualize(object):
    def __init__(self):
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument(
            '-f',
            '--feature_filename',
            dest='feature_filename',
            type=str,
            help='The name of the feature file (json)',
            required=True
        )
        arg_parser.add_argument(
            '-s',
            '--sound_filename',
            dest='sound_filename',
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
        with open(os.path.join('feature_data', self.args.feature_filename)) as data_file:
            self.feature_data = json.load(data_file)

    def run(self):
        self.gfx = Gfx(
            self.feature_data['series'],
            self.feature_data['krate'],
            os.path.join('input', self.args.sound_filename)
        )
        self.gfx.start_sound()

        for i in xrange(2000):
            self.gfx.draw()


if __name__ == '__main__':
    #pygame.display.init()
    pygame.init()
    Visualize()
