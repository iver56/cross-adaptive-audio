import argparse
import neuroevolution


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '-i',
        '--input',
        dest='input_files',
        nargs='+',
        type=str,
        help='The filename of the target sound and'
             ' the filename of the input sound, respectively',
        required=True,
        default=[]
    )
    arg_parser.add_argument(
        '-g',
        '--num-generations',
        dest='num_generations',
        type=int,
        required=False,
        default=20
    )
    arg_parser.add_argument(
        '-p',
        '--population_size',
        dest='population_size',
        type=int,
        required=False,
        default=20
    )
    arg_parser.add_argument(
        '--patience',
        dest='patience',
        help='Number of generations with no improvement in similarity before stopping',
        type=int,
        required=False,
        default=100
    )
    arg_parser.add_argument(
        '-s',
        '--seed',
        dest='seed',
        help='PRNG seed. Will be set to a random value if not specified.',
        type=int,
        required=False,
        default=-1  # -1 means the seed will be random for each run
    )
    arg_parser.add_argument(
        '--keep-k-best',
        dest='keep_k_best',
        help='Store only the k fittest individual in each generation. Improves perf and'
             ' saves storage. If set to 0, no individuals will be stored.',
        type=int,
        required=False,
        default=-1  # -1 means keep all
    )
    arg_parser.add_argument(
        '--keep-all-last',
        nargs='?',
        dest='keep_all_last',
        help='Store all individuals in the last generation, disregarding --keep-k-best in'
             ' that generation',
        const=True,
        required=False,
        default=False
    )
    arg_parser.add_argument(
        '--allow-clones',
        nargs='?',
        dest='allow_clones',
        help="""Allow clones or nearly identical genomes to exist simultaneously in the
                    population. This is useful for non-deterministic environments,
                    as the same individual will get more than one chance to prove himself, also
                    there will be more chances the same individual to mutate in different ways.
                    The drawback is greatly increased time for reproduction. If you want to
                    search quickly, yet less efficient, leave this to true.""",
        const=True,
        required=False,
        default=False
    )
    arg_parser.add_argument(
        '--add-neuron-prob',
        dest='add_neuron_probability',
        type=float,
        help='MutateAddNeuronProb: Probability for a baby to be mutated with the'
             ' Add-Neuron mutation',
        required=False,
        default=0.03
    )
    arg_parser.add_argument(
        '--add-link-prob',
        dest='add_link_probability',
        type=float,
        help='MutateAddLinkProb: Probability for a baby to be mutated with the'
             ' Add-Link mutation',
        required=False,
        default=0.03
    )
    arg_parser.add_argument(
        '--rem-link-prob',
        dest='remove_link_probability',
        type=float,
        help='MutateRemLinkProb: Probability for a baby to be mutated with the'
             ' Remove-Link mutation',
        required=False,
        default=0.06
    )
    arg_parser.add_argument(
        '--rem-simple-neuron-prob',
        dest='remove_simple_neuron_probability',
        type=float,
        help='MutateRemSimpleNeuronProb: Probability for a baby that a simple neuron'
             ' will be replaced with a link',
        required=False,
        default=0.03
    )
    arg_parser.add_argument(
        '--elitism',
        dest='elitism',
        type=float,
        help='Fraction of population to carry on to the next generation unaltered',
        required=False,
        default=0.1
    )
    arg_parser.add_argument(
        '--fs-neat',
        nargs='?',
        dest='fs_neat',
        help='Use FS-NEAT (automatic feature selection)',
        const=True,
        required=False,
        default=False
    )
    arg_parser.add_argument(
        '--neural-input-mode',
        dest='neural_input_mode',
        type=str,
        choices=['a', 'ab', 'b', 's'],
        help='What to use as neural input. Mode a: target sound. Mode ab: target sound and'
             ' input sound. Mode b: input sound. Mode s: static input, i.e. only bias.',
        required=False,
        default="a"
    )
    arg_parser.add_argument(
        '--output-activation-function',
        dest='output_activation_function',
        type=str,
        choices=['sigmoid', 'linear', 'sine'],
        help='Activation function of output nodes in the neural networks',
        required=False,
        default="sigmoid"
    )
    arg_parser.add_argument(
        '--fitness',
        dest='fitness',
        type=str,
        help='similarity: Average local similarity, calculated with euclidean distance between'
             ' feature vectors for each frame. multi-objective optimizes for a diverse'
             ' population that consists of various non-dominated trade-offs between similarity'
             ' in different features. Hybrid fitness is the sum of similarity and multi-objective,'
             ' and gives you the best of both worlds. Novelty fitness ignores the objective and'
             ' optimizes for novelty. Mixed fitness chooses a random fitness evaluator for each'
             ' generation.',
        choices=['similarity', 'multi-objective', 'hybrid', 'novelty', 'mixed'],
        required=False,
        default="similarity"
    )
    arg_parser.add_argument(
        '--effect',
        dest='effect_name',
        type=str,
        help='The name of the sound effect to use. See the effects folder for options.',
        required=False,
        default="dist_lpf"
    )
    arg_parser.add_argument(
        '--num-runs',
        dest='num_runs',
        help='Number of times to run the experiment (makes sense if seed is not specified)',
        type=int,
        required=False,
        default=1
    )
    args = arg_parser.parse_args()

    num_runs = args.num_runs
    del args.num_runs
    for i in range(num_runs):
        if num_runs > 1:
            print('')
            print('------')
            print('Run {}'.format(i + 1))
            print('------')
        neuroevolution.Neuroevolution(args)
