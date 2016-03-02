"""
Based on https://github.com/peter-ch/MultiNEAT/blob/master/MultiNEAT/viz.py
"""

from _MultiNEAT import *
import numpy as np


def is_almost_equal(a, b, margin):
    if abs(a - b) > margin:
        return False
    else:
        return True


def get_neural_network_representation(nn, is_substrate=False):
    # if this is a genome, make a NN from it
    if type(nn) == Genome:
        kk = NeuralNetwork()
        nn.BuildPhenotype(kk)
        nn = kk

    if is_substrate:
        raise Exception('Not implemented for substrates')

    # not a substrate, compute the node coordinates
    for i, n in enumerate(nn.neurons):
        nn.neurons[i].x = 0
        nn.neurons[i].y = 0

    rect_x = 0.0
    rect_y = 0.0
    rect_x_size = 1.0
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
    for neuron in nn.neurons:
        type_label = ''
        if neuron.type == NeuronType.INPUT:
            type_label = 'input'
        elif neuron.type == NeuronType.BIAS:
            type_label = 'bias'
        elif neuron.type == NeuronType.HIDDEN:
            type_label = 'hidden'
        elif neuron.type == NeuronType.OUTPUT:
            type_label = 'output'

        neurons.append({
            'id': 'n{}'.format(i),
            'x': neuron.x,
            'y': neuron.y,
            'size': neuron_radius,
            'label': type_label
        })
        i += 1

    connections = []
    i = 0
    for connection in nn.connections:
        connections.append({
            'id': 'e{}'.format(i),
            'source': 'n{}'.format(connection.source_neuron_idx),
            'target': 'n{}'.format(connection.target_neuron_idx)
        })
        i += 1

    return {
        'nodes': neurons,
        'edges': connections
    }
