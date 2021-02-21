# -*- coding: utf-8 -*-

import random
from Plugins import PluginManager
import configparser
import numpy as np

config = configparser.ConfigParser()
config.read('config.ini')

ActivationFunctions = PluginManager.importPlugins('ActivationFunc')
ErrorFunctions = PluginManager.importPlugins('ErrorFunc')


class Neuron:

    # TotalNeurons is an incrementing int which keeps track of how many neurons have been created for naming

    TotalNeurons = 0

    # w is an array containing weights (ints)
    # @param Bias is a float
    # @param LearningRate is a float
    # @param activationFunction is a string

    def __init__(
        self,
        LearningRate,
        activationFunction,
        errorFunction,
        ):
        self.name = Neuron.TotalNeurons
        Neuron.TotalNeurons += 1
        self.a = float(0)  # Activation
        self.w = []  # Weights
        self.b = random.uniform(-1, 1)  # Bias
        self.R = LearningRate  # Learning Rate
        self.actFunc = activationFunction
        self.errFunc = errorFunction

    def __repr__(self):
        div = '+--------------------------------+'
        String = div + '\n|Neuron:%25s|' % self.name
        String += '''
|Activation:%21g|
''' % self.a
        String += '|Bias:%27g|\n' % self.b
        for i in range(len(self.w)):
            String = String + '|Weight %3s' % ('x' + str(i)) \
                + ':%21g|\n' % self.w[i]
        String = String + '+--------------------------------+'
        return String

    # Sets the activation function to be used
    # @param ActivationFunc is a string

    def setActivationFunc(self, ActivationFunc):
        if PluginManager.checkTypeValid(ActivationFunc):
            self.actFunc = ActivationFunc

    # returns activation using the given weights and biases
    # If weights don't exist, generate them randomly. This allows undetermined number of inputs
    # @param inputArray is an array of floats

    def activate(self, inputArray):
        if self.w == []:
            y = 1 / np.sqrt(len(inputArray))
            for i in range(len(inputArray)):
                self.w.append(random.uniform(-y, y))
            self.w = np.array(self.w)
        inputs = np.array(inputArray)
        activation = getattr(ActivationFunctions[self.actFunc], 'Func'
                             )(sum(inputs * self.w) + self.b)
        self.a = activation
        return self.a

    # The following function calculates the weights of the neuron and the bias,
    # then returns deltaError + deltaAct, and new weights for backward propegation
    # @param inputs is an array of floats
    # @param expectedOutput is a float
    # @param layerType is a string

    def calcWeights(
        self,
        inputs,
        expectedOutput,
        layerType,
        ):
        newWeights = self.w

        deltaAct = getattr(ActivationFunctions[self.actFunc],
                           'FuncPrime')(self.a)

        # deltaError is the expectedOutput if the neuron belongs to a hidden
        # layer. the expectedOutput is the sum deltaError*deltaAct of neurons
        # in the next layer.

        if layerType == 'hidden' or layerType == 'input':
            deltaError = np.array(expectedOutput)
            inputs = np.array(inputs)

            # Calculate New Weights

            delta = deltaError * deltaAct * inputs * self.R
            newWeights = np.subtract(newWeights, delta)
        elif layerType == 'output':

            deltaError = getattr(ErrorFunctions[self.errFunc],
                                 'FuncPrime')(self.a, expectedOutput)
            inputs = np.array(inputs)

            # Calculate New Weights

            delta = deltaError * deltaAct * inputs * self.R
            newWeights = np.subtract(newWeights, delta)
        else:

            raise ValueError('"layerType" has to be "hidden" or "output" ("hidden" is default)'
                             )

        return [deltaError * deltaAct, newWeights]  # Missing weight here

    # returns the delta error of the neuron
    # @param expectedOutput is a float
    # @param layerType is a string

    def calcBias(self, expectedOutput, layerType='hidden'):
        if layerType == 'output':
            deltaBias = getattr(ErrorFunctions[self.errFunc],
                                'FuncPrime')(self.a, expectedOutput) \
                * getattr(ActivationFunctions[self.actFunc], 'FuncPrime'
                          )(self.a) * self.R
        else:
            deltaBias = expectedOutput \
                * getattr(ActivationFunctions[self.actFunc], 'FuncPrime'
                          )(self.a) * self.R
        newBias = self.b - deltaBias
        return newBias
