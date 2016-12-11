import argparse
import json
import os
import settings
import numpy as np
import matplotlib.pyplot as plt


class Plot(object):
    def __init__(self):
        arg_parser = argparse.ArgumentParser()

        arg_parser.add_argument(
            '--dimensions',
            dest='dimensions',
            type=str,
            nargs='+',
            help='Which args to use as the two dimensions',
            required=True
        )
        arg_parser.add_argument(
            '--output',
            dest='output',
            help='Output image file (PNG). If specified, interactive window will not appear.',
            required=False,
            default=None
        )
        args = arg_parser.parse_args()

        experiments = {}

        for root, dirs, files in os.walk(settings.STATS_DATA_DIRECTORY):
            if dirs:
                for experiment_dir in dirs:
                    if 'test' in experiment_dir:
                        continue
                    stats_file_path = os.path.join(
                        settings.STATS_DATA_DIRECTORY,
                        experiment_dir,
                        'stats.json'
                    )
                    if os.path.exists(stats_file_path):
                        experiment_id = experiment_dir.split('__')[1]
                        if experiment_id not in experiments:
                            experiments[experiment_id] = []
                        experiments[experiment_id].append(stats_file_path)

        values = []
        positions = []
        for experiment_id in experiments:
            stats_data_objects = []
            for stats_file_path in experiments[experiment_id]:
                with open(stats_file_path) as stats_file:
                    stats = json.load(stats_file)
                    stats_data_objects.append(stats)

            experiment_series = []  # series for this experiment
            for stats_data_object in stats_data_objects:
                # compute cumulative maximum similarity
                max_similarity = stats_data_object['generations'][0]['similarity_max']
                similarity_series = []
                for generation in stats_data_object['generations']:
                    if generation['similarity_max'] > max_similarity:
                        max_similarity = generation['similarity_max']
                    similarity_series.append(max_similarity)

                experiment_series.append(similarity_series)

            # take the average of the last generation in the experiment series
            last_generation = len(experiment_series[0]) - 1
            avg_similarity = sum(series[last_generation] for series in experiment_series) / len(
                experiment_series)
            values.append(avg_similarity)

            key = (
                stats_data_objects[0]['args'][args.dimensions[0]],
                stats_data_objects[0]['args'][args.dimensions[1]]
            )
            positions.append(key)

        dimension1_values = sorted(set(key[0] for key in positions))
        dimension1_indexes = {value: i for i, value in enumerate(dimension1_values)}
        dimension1_range = dimension1_values[-1] - dimension1_values[0]
        dimension1_step = dimension1_range / len(dimension1_values)
        print(args.dimensions[0], dimension1_values)

        dimension2_values = sorted(set(key[1] for key in positions))
        dimension2_indexes = {value: i for i, value in enumerate(dimension2_values)}
        dimension2_range = dimension2_values[-1] - dimension2_values[0]
        dimension2_step = dimension2_range / len(dimension2_values)
        print(args.dimensions[1], dimension2_values)

        image = np.zeros(
            shape=(
                len(dimension1_values),
                len(dimension2_values)
            )
        )

        for i, value in enumerate(values):
            position = positions[i]
            dimension1_index = dimension1_indexes[position[0]]
            dimension2_index = dimension2_indexes[position[1]]
            print(position, value, dimension1_index, dimension2_index)

            image[dimension1_index, dimension2_index] = value

        print(image)

        fig, ax = plt.subplots()

        img = ax.imshow(
            image,
            extent=[
                dimension2_values[0] - 0.5 * dimension2_step,
                dimension2_values[-1] + 0.5 * dimension2_step,
                dimension1_values[0] - 0.5 * dimension1_step,
                dimension1_values[-1] + 0.5 * dimension1_step
            ],
            cmap=plt.cm.viridis,
            interpolation='nearest',
            origin='lower'
        )
        #ax.set_title('Heat map')

        # Move left and bottom spines outward by 10 points
        ax.spines['left'].set_position(('outward', 10))
        ax.spines['bottom'].set_position(('outward', 10))
        # Hide the right and top spines
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # Only show ticks on the left and bottom spines
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')

        ax.set_xticks(dimension2_values)
        ax.set_yticks(dimension1_values)

        ax.set_xlabel(args.dimensions[1])
        ax.set_ylabel(args.dimensions[0])

        cb = plt.colorbar(img, ax=ax, ticks=[min(values), max(values)])
        cb.set_label('Fitness value')

        if args.output is None:
            plt.show()
        else:
            plt.savefig(args.output, dpi=300)


if __name__ == "__main__":
    Plot()
