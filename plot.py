import argparse
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import os
import settings


class Plot(object):
    """
    Plot cumulative max similarity for all experiments
    """
    def __init__(self):

        # Python 2 and 3 compatibility hack
        try:
            input = raw_input
        except NameError:
            pass

        arg_parser = argparse.ArgumentParser()

        arg_parser.add_argument(
            '--small-font',
            nargs='?',
            dest='small_font',
            help='Use a small font in the legend',
            const=True,
            required=False,
            default=False
        )
        arg_parser.add_argument(
            '--label',
            dest='label',
            help='Which arg to use as label',
            required=False,
            default=None
        )
        arg_parser.add_argument(
            '--output',
            dest='output',
            help='Output image file (PNG). If specified, interactive window won\t appear.',
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

        all_series = []
        all_series_labels = []
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

            # take the average of experiment series
            avg_similarity = []
            for k in range(len(experiment_series[0])):
                avg = 0.0
                for series in experiment_series:
                    avg += series[k]
                avg /= len(experiment_series)
                avg_similarity.append(avg)
            all_series.append(avg_similarity)

            if args.label is None:
                print(stats_data_objects[0]['args'])
                label = input('label name? ')
                all_series_labels.append(label)
            else:
                all_series_labels.append(stats_data_objects[0]['args'][args.label])

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title('Best individual')
        ax.set_ylabel('similarity measure')

        handles = []

        for i, series in enumerate(all_series):
            x = np.array(range(len(series)))
            series_plot, = plt.plot(x, np.array(series), label=all_series_labels[i])
            handles.append(series_plot)

        font_p = FontProperties()
        if args.small_font:
            font_p.set_size('small')
        plt.legend(handles=handles, prop=font_p, loc='best')

        ax.set_xlabel('# generations')

        if args.output is None:
            plt.show()
        else:
            plt.savefig(args.output, dpi=300)


if __name__ == "__main__":
    Plot()
