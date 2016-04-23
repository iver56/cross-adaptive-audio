"""
Based on https://github.com/peter-ch/MultiNEAT/blob/master/MultiNEAT/viz.py
"""

from _MultiNEAT import *
import numpy as np
import analyze
import cross_adapt


def is_almost_equal(a, b, margin):
    if abs(a - b) > margin:
        return False
    else:
        return True


def get_neural_network_representation(nn, neural_input_mode, is_substrate=False):
    # if this is a genome, make a NN from it
    if type(nn) == Genome:
        kk = NeuralNetwork()
        nn.BuildPhenotype(kk)
        nn = kk

    if is_substrate:
        raise Exception('Not implemented for substrates')

    # not a substrate, compute the node coordinates
    for i, n in enumerate(nn.neurons):
        nn.neurons[i].x = 0.0
        nn.neurons[i].y = 0.0

    rect_x = 0.0
    rect_y = 0.0
    rect_x_size = 3.0
    rect_y_size = 1.0
    neuron_radius = 0.03

    MAX_DEPTH = 64

    # for every depth, count how many nodes are on this depth
    all_depths = np.linspace(0.0, 1.0, MAX_DEPTH)

    for depth in all_depths:
        neuron_count = 0
        for neuron in nn.neurons:
            if is_almost_equal(neuron.split_y, depth, 1.0 / (MAX_DEPTH + 1)):
                neuron_count += 1
        if neuron_count == 0:
            continue

        # calculate x positions of neurons
        xxpos = rect_x_size / (1 + neuron_count)
        j = 0
        for neuron in nn.neurons:
            if is_almost_equal(neuron.split_y, depth, 1.0 / (MAX_DEPTH + 1)):
                neuron.x = rect_x + xxpos + j * (rect_x_size / (2 + neuron_count))
                j += 1

    # calculate y positions of nodes
    for neuron in nn.neurons:
        base_y = rect_y + neuron.split_y
        size_y = rect_y_size - neuron_radius

        if neuron.split_y == 0.0:
            neuron.y = base_y * size_y + neuron_radius
        else:
            neuron.y = base_y * size_y

    neurons = []
    i = 0
    counter = {
        'unknown': 0,
        'input': 0,
        'bias': 0,
        'hidden': 0,
        'output': 0
    }
    for neuron in nn.neurons:
        neuron_type = 'unknown'
        if neuron.type == NeuronType.INPUT:
            neuron_type = 'input'
        elif neuron.type == NeuronType.BIAS:
            neuron_type = 'bias'
        elif neuron.type == NeuronType.HIDDEN:
            neuron_type = 'hidden'
        elif neuron.type == NeuronType.OUTPUT:
            neuron_type = 'output'

        label = neuron_type
        if neuron_type == 'input':
            if neural_input_mode == 'ab':
                prefix = 't_' if counter['input'] / analyze.Analyzer.NUM_FEATURES < 1 else 'i_'
                idx = counter['input'] % analyze.Analyzer.NUM_FEATURES
                label = prefix + analyze.Analyzer.FEATURES_LIST[idx]
            elif neural_input_mode == 'a':
                label = 't_' + analyze.Analyzer.FEATURES_LIST[counter['input']]
            else:  # neural_input_mode == 'b'
                label = 'i_' + analyze.Analyzer.FEATURES_LIST[counter['input']]
        elif neuron_type == 'output':
            label = cross_adapt.CrossAdapter.PARAMETER_LIST[counter['output']]

        counter[neuron_type] += 1

        neurons.append({
            'id': 'n{}'.format(i),
            'x': neuron.x,
            'y': neuron.y,
            'size': neuron_radius,
            'label': label,
            'type': neuron_type
        })
        i += 1

    connections = []
    i = 0
    for connection in nn.connections:
        connections.append({
            'id': 'e{}'.format(i),
            'source': 'n{}'.format(connection.source_neuron_idx),
            'target': 'n{}'.format(connection.target_neuron_idx),
            'weight': connection.weight
        })
        i += 1

    return {
        'nodes': neurons,
        'edges': connections
    }
