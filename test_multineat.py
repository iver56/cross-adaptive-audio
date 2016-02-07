from __future__ import absolute_import
import unittest
import MultiNEAT as NEAT


class TestMultiNeat(unittest.TestCase):
    def evaluate(self, genome):
        # this creates a neural network (phenotype) from the genome

        net = NEAT.NeuralNetwork()
        genome.BuildPhenotype(net)

        # let's input just one pattern to the net, activate it once and get the output
        # The last input is always used as bias and also when you activate the network always set the last input to 1.0
        net.Input([1.0, 0.0, 1.0])
        net.Activate()
        output = net.Output()

        # the output can be used as any other Python iterable. For the purposes of the tutorial,
        # we will consider the fitness of the individual to be the neural network that outputs constantly
        # 0.0 from the first output (the second output is ignored)

        fitness = 1.0 - output[0]
        return fitness

    def test_multi_neat(self):
        params = NEAT.Parameters()
        params.PopulationSize = 100
        genome = NEAT.Genome(
            0,
            3,  # number of inputs. Note: always add one extra input, according to http://multineat.com/docs.html
            0,
            2,  # number of outputs
            False,
            NEAT.ActivationFunction.UNSIGNED_SIGMOID,
            NEAT.ActivationFunction.UNSIGNED_SIGMOID,
            0,
            params
        )
        pop = NEAT.Population(
            genome,
            params,
            True,  # whether the population should be randomized
            1.0,  # how much the population should be randomized,
            1  # seed for a pseudo-random number generator, perhaps?
        )

        for generation in range(100):  # run for 100 generations
            # retrieve a list of all genomes in the population
            genome_list = NEAT.GetGenomeList(pop)

            # apply the evaluation function to all genomes
            for genome in genome_list:
                fitness = self.evaluate(genome)
                genome.SetFitness(fitness)

            # at this point we may output some information regarding the progress of evolution, best fitness, etc.
            # it's also the place to put any code that tracks the progress and saves the best genome or the entire
            # population. We skip all of this in the tutorial.

            # advance to the next generation
            pop.Epoch()


if __name__ == '__main__':
    unittest.main()
