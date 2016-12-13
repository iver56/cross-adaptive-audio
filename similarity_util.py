import argparse
import project
import sound_file
import fitness
import experiment
import analyze


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '-i',
        '--input',
        dest='input_files',
        nargs=3,
        type=str,
        help='The filenames of target sound, input sound and output sound respectively',
        required=True
    )
    arg_parser.add_argument(
        '--experiment-settings',
        dest='experiment_settings',
        type=str,
        help='Filename of json file in the experiment_settings folder. This file specifies which'
             ' features to use as neural input and for similarity calculations.',
        required=False,
        default="mfcc_basic.json"
    )
    args = arg_parser.parse_args()

    experiment.Experiment.load_experiment_settings(args.experiment_settings)
    analyze.Analyzer.init_features_list()

    target_sound = sound_file.SoundFile(args.input_files[0], is_input=True, verify_file=True)
    input_sound = sound_file.SoundFile(args.input_files[1], is_input=True, verify_file=True)
    output_sound = sound_file.SoundFile(args.input_files[2], is_input=False, verify_file=True)
    that_project = project.Project([target_sound, input_sound])
    analyzer = analyze.Analyzer(that_project)

    analyzer.analyze_multiple([output_sound])

    similarity_score = fitness.LocalSimilarityFitness.get_local_similarity(target_sound, output_sound)
    print(similarity_score)
