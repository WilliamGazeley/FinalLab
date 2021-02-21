# -*- coding: utf-8 -*-

import NeuralNetwork.Neuron as Neuron
import configparser
import numpy as np

config = configparser.ConfigParser()
config.read('config.ini')


class Layer:

    # layerNum is an incrementing int which keeps track of how many neurons have been created for naming

    layerNum = 0

    # @param Neurons is 2D array [[neuron params],[neuron params],...]
    # Accept array of neurons or just a number for the num of neurons for the layer

    def __init__(
        self,
        Neurons,
        LearningRate,
        activationFunction,
        errorFunction,
        name=None,
        ):
        self.Layer = []
        self.R = LearningRate
        self.outputs = []  # an array of activations for the layer for quick referencing
        self.neuronCount = 0
        if name == None:
            self.name = Layer.layerNum
        else:
            self.name = name
        if isinstance(Neurons, int):
            for i in range(Neurons):
                newNeuron = Neuron.Neuron(LearningRate,
                        activationFunction, errorFunction)
                self.Layer.append(newNeuron)
                self.outputs.append(0)
                self.neuronCount += 1
        else:

              # Can break here because parameters NEED to be orders. Not robust

            for neuronParams in Neurons:
                if len(neuronParams) == 1:
                    newNeuron = Neuron.Neuron(neuronParams[0])
                elif len(neuronParams) == 2:
                    newNeuron = Neuron.Neuron(neuronParams[0],
                            neuronParams[1])
                else:
                    newNeuron = Neuron.Neuron(neuronParams[0],
                            neuronParams[1], neuronParams[2])
                self.Layer.append(newNeuron)
                self.outputs.append(0)
                self.neuronCount += 1
        Layer.layerNum += 1

    def __repr__(self):
        div = '+================================+\n'
        String = '\n' + div + '|Layer: {:-25d}|\n'.format(self.name) \
            + div
        for neuron in self.Layer:
            String = String + str(neuron) + '\n'
        String += div
        return String

    # Takes an array of inputs, overwrites, and returns output of neurons in the layer as an array
    # @param inputs is an array of ints

    def run(self, inputs):
        outputs = []
        for i in range(0, len(self.Layer)):
            outputs.append(self.Layer[i].activate(inputs))
        self.outputs = outputs
        return self.outputs

    # Calculates weights and bias in layer then returns:
    # new weights, and SUM(errPrime*actPrime*w) for all neurons in layer
    # @param inputs is an array of floats
    # @param expectedOutputs is an array of floats. Also can be errPrimes of layer n+1
    # @param layerType is a string

    def calcUpdates(
        self,
        inputs,
        expectedOutputs,
        layerType,
        ):

        # newWeights is a 2d array to hold new weights for after all calculations are complete
        # oldWeights is a 2d array of weights used to calculate final errPrimes for return. len is = neurons in current layer, vals are weights leading into currentlayer+1
        # errPrimes is an array of sumed errPrime*actPrime of all neurons in current layer

        newWeights = []
        oldWeights = []
        errPrimes = []

        # Collect Old Weights

        oldWeights = self.Layer[0].w
        for i in range(1, len(self.Layer)):
            oldWeights = np.vstack((oldWeights, self.Layer[i].w))
        oldWeights = np.column_stack(oldWeights)

        # Layer types for validation

        validLayerTypes = ['input', 'hidden', 'output']

        # Calculate the new weights

        if layerType in validLayerTypes:
            for neuron in range(0, len(self.Layer)):

                # results is an array:
                # [0] array of new calculated weights
                # [1] errPrime*actPrime of the neuron

                results = self.Layer[neuron].calcWeights(inputs,
                        expectedOutputs[neuron], layerType=layerType)
                errPrimes.append(results[0])
                newWeights.append(results[1])
        else:
            raise ValueError('layerType invalid')

        # Calculate errPrimes using oldWeights

        errPrimes = np.array(errPrimes)

        if len(errPrimes) == 1:
            oldWeights = np.column_stack(oldWeights)
        newErrPrimes = oldWeights.dot(errPrimes)

        return [newWeights, newErrPrimes]

    # Updates the weights and bias of the layer
    # @param weights is a 2d array of new weights
    # @param bias is an array of new bias

    def updateWeights(self, weights):
        for (i, neuron) in enumerate(self.Layer):
            neuron.w = weights[i]
        return

    # Updates bias using errPrime
    # @param errPrime is an array of [SUM(errPrime*actPrime*w), ...] for each layer in n+1 for use in layer n
    # @param layerType is the (string) layer type

    def updateBias(self, errPrime, layerType='hidden'):
        for (i, neuron) in enumerate(self.Layer):
            neuron.b = neuron.calcBias(errPrime[i], layerType=layerType)
        return
