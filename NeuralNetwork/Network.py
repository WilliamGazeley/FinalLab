# -*- coding: utf-8 -*-

from NeuralNetwork.Layer import Layer
from NeuralNetwork.Neuron import Neuron
from Plugins.ActivationFunc_sigmoid import Func
from Data import DataManager
import configparser
import gzip
import pickle

config = configparser.ConfigParser()
config.read('config.ini')
import numpy as np


class Network:

    # @param InputArray is an array of integers, which determines how many neurons in each layer
    # @param LearningRate is the learning rate the network is initialised with (float)
    # @param activationFunction name of the activation function the network is initialised with (string)
    # @param errorFunction is the name of the error function the network is initialised with (string)
    # Network is an array of layer objs
    # inputs is a list of inputs from last time Network was run
    # outputs is a list of outputs of the final layer from the last time Network was run
    # accuracy is an array of the accuracy of the network on the previouslt run test

    def __init__(
        self,
        InputArray,
        LearningRate=2.4,
        activationFunction='sigmoid',
        errorFunction='MSE',
        ):
        if len(InputArray) != 0:
            if not isinstance(InputArray, list) or not ''.join([str(x)
                    for x in InputArray]).replace('.', '').isdigit():
                raise TypeError('"InputArray" must be an array of integers'
                                )

        self.structure = InputArray
        self.Network = []
        self.inputs = []
        self.outputs = []
        self.accuracy = 0
        Layer.layerNum = 0
        Neuron.TotalNeurons = 0

        for i in range(0, len(InputArray)):
            newLayer = Layer(InputArray[i], LearningRate,
                             activationFunction, errorFunction)
            self.Network.append(newLayer)
        return

    def __repr__(self):
        div = '||' + len(self.Network) * ('-' * 22 + '||') + '\n'
        String = div + '||'
        mostNeurons = self.getMostNeurons()
        for i in range(len(self.Network)):
            String += ' Layer: %-14s' % self.Network[i].name + '||'
        else:
            String += '\n' + div + '||'

        for i in range(len(self.Network)):
            String += ' Neurons: %-12d' % self.Network[i].neuronCount \
                + '||'
        else:
            String += '\n'
        for i in range(mostNeurons):
            for j in range(len(self.Network)):
                try:
                    String += '|| Neur %d Out: %-9f' % (i,
                            self.Network[j].outputs[i])
                except:
                    String += '||' + ' ' * 22
            else:
                String += '||\n'
        String += div[:-1]
        return String

    # Auxillary function for __repr__
    # returns largest no. of neurons in a layer

    def getMostNeurons(self):
        mostNeurons = 0
        for layer in self.Network:
            if mostNeurons < layer.neuronCount:
                mostNeurons = layer.neuronCount
        return mostNeurons

    # Takes array of inputs and 1) checks the array == input layer size 2) gets network output 3) saves input and output
    # @param inputs is an array of ints
    # @param normalise is a boolean that normalises the input using the activation function

    def forwardProp(self, inputs, normalise=True):

        # Validate inputs

        if not (isinstance(inputs, np.ndarray) or isinstance(inputs,
                list)) or not ''.join([str(x) for x in
                inputs]).replace('.', '').isdigit():
            raise TypeError('"inputs" must be an array of floats or ints'
                            )
        elif not (len(self.inputs) == 0 or len(self.inputs)
                  == len(self.inputs)):
            raise TypeError('"inputs" is the incorrect length')

        # Save inputs

        if normalise == True:
            normalise = np.vectorize(Func)
            inputs = normalise(inputs)
        self.inputs = inputs

        # forward propagate (output of one layer is input of the next)

        for i in range(0, len(self.Network)):
            inputs = self.Network[i].run(inputs)

        # Save outputs

        self.outputs = self.Network[len(self.Network) - 1].outputs

        return self.outputs

    # Takes array of inputs and 1) checks the array == input layer size 2) Propagates backwards
    # @param inputs is an array of ints
    # @param expectedOutputs is an array of ints

    def backwardProp(self, expectedOutputs):

        # Validate inputs

        if not isinstance(expectedOutputs, np.ndarray) \
            or not ''.join([str(x) for x in
                           expectedOutputs]).replace('.', '').isdigit():
            raise TypeError('"expectedOutputs" must be an array of ints'
                            )
        elif not (len(self.outputs) == 0 or len(expectedOutputs)
                  == len(self.outputs)):
            raise TypeError('"expectedOutputs" is the incorrect length')

        # newWeights is a 2d array to hold newly calculated weights

        newWeights = []

        # OUTPUT LAYER
        # new weights needs: inputs to layer, outputs of layer, expectedOuts, SUM(errPrime*actPrime*w) of next layer
        # results is an array:
        # [0] 2d array of new weights
        # [1] array of errPrimes (len will be same as neurons in layer n-1)

        results = \
            self.Network[-1].calcUpdates(self.Network[-2].outputs,
                expectedOutputs, layerType='output')
        newWeights = results[0]
        self.Network[-1].updateWeights(newWeights)
        self.Network[-1].updateBias(expectedOutputs, layerType='output')

        # update errPrimes for hidden layer
        # errPrime is an array of SUM(errPrime*actPrime*w) of each neuron in layer n, TO each neuron in layer n-1

        errPrimes = results[1]

        # HIDDEN LAYERS

        for layer in range(len(self.Network) - 2, 0, -1):
            results = \
                self.Network[layer].calcUpdates(self.Network[layer
                    - 1].outputs, errPrimes, layerType='hidden')
            newWeights = results[0]
            self.Network[layer].updateWeights(newWeights)
            self.Network[layer].updateBias(errPrimes)
            errPrimes = results[1]

        # INPUT LAYERS

        results = self.Network[0].calcUpdates(self.inputs, errPrimes,
                layerType='input')
        newWeights = results[0]
        self.Network[0].updateWeights(newWeights)
        self.Network[0].updateBias(errPrimes)

    # Does exactly what you expect it to do.
    # @param NN is the Neural network to be trained
    # @param data is a (string) path to the data to be trained with
    # @param expecteds is a (string) path to the labels for backprop
    # @param progressBar is a ttk.Progressbar obj to be updated
    # @param stopBtn and closeBtn are Tk.Button objs
    # @param window is a Tk.Toplevel obj
    # @param instance is the instance of trainingWindow obj
    # @param normalise is a bool determining if inputs in forwardpass should be normalised using the sigmoid function

    def train(
        self,
        data,
        expecteds,
        window,
        normalise=False,
        ):

        # Get image size, and num of images from data

        imgCount = DataManager.getSetSize(data)
        imgSize = DataManager.getImgSize(data)

        # Get label file ready

        expecteds = gzip.open(expecteds, 'r')
        expecteds.read(8)  # get past headers

        # Get images and train

        data = gzip.open(data, 'r')
        for i in range(0, imgCount):

            # print('Training on Image: ', i+1)

            # Build image array

            buffer = data.read(imgSize)
            image = np.frombuffer(buffer, dtype=np.uint8)

            # One hot encode label

            label = int.from_bytes(expecteds.read(1), byteorder='big')
            expectedOutput = np.zeros(10)
            expectedOutput[label] = 1

            # Update progress bar

            window.progressBar['value'] += 1
            window.window.update()

            # Do passes

            self.forwardProp(image, normalise=normalise)
            self.backwardProp(expectedOutput)

            # Check if training should be stopped

            if window.stop == True:
                break

        # Setup window things

        window.progressLabel['text'] = 'Progress: Complete!'

        # Free resources

        data.close()
        expecteds.close()

        return

    # @param data is a string path to images
    # @param expecteds is a string path to labels
    # @window is a TestingWindow.testingWindow obj

    def test(
        self,
        data,
        expecteds,
        window,
        ):

        # Get image size, and num of images from data

        data = gzip.open(data, 'r')
        data.read(4)  # get past magic number
        imgCount = int.from_bytes(data.read(4), byteorder='big')
        imgSize = int.from_bytes(data.read(4), byteorder='big') \
            * int.from_bytes(data.read(4), byteorder='big')

        # Get label file ready

        expecteds = gzip.open(expecteds, 'r')
        expecteds.read(8)  # get past headers

        # Setup result array
        # [n] results for digit n
        # [n][0] total instances of digit
        # [n][1] total correct classifications
        # [n][2] accuracy

        result = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            ]

        # Start test

        for i in range(imgCount):

            # Build image array

            buffer = data.read(imgSize)
            image = np.frombuffer(buffer, dtype=np.uint8)

            # Get label and add to the result count

            label = int.from_bytes(expecteds.read(1), byteorder='big')
            result[label][0] += 1

            self.forwardProp(image)
            output = self.outputs.index(max(self.outputs))

            # Add to result correct count if classification correct

            if output == label:
                result[label][1] += 1

            # Update progress window

            window.progressBar['value'] += 1
            window.window.update()

            if window.stop == True:
                break

        # Add results to window.table

        for i in range(10):

            # Calculate Accuracy

            if result[i][1] == 0:  # To prevent division by 0
                result[i][2] = 0
            else:
                result[i][2] = result[i][1] / result[i][0] * 100

            # Create row

            row = [result[i][0], result[i][1],
                   '{:.2f}%'.format(result[i][2])]

            # Insert row

            window.table.insert('', i + 1, text=str(i), values=row)

        # Calculate totals

        result = np.array(result)
        result = np.column_stack(result)

        totalInstances = str(result[0].sum())
        totalCorrect = str(result[1].sum())
        totalAccuracy = '{:.2f}'.format(result[2].sum() / 10)

        # Insert totals row

        row = [totalInstances, totalCorrect, str(totalAccuracy) + '%']
        window.table.insert('', 11, text='Totals', values=row)

        return

    # Write to a file the current model
    # @param path is the String location of where to write the file

    def export(self, path):
        if path == '':
            return
        else:
            file = open(path, 'wb')
            pickle.dump(self, file)
            file.close()
            return
