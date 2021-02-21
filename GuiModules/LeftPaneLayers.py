# -*- coding: utf-8 -*-

import tkinter as Tk
from tkinter import ttk
import NeuralNetwork.Network as Network
import Globals
from GuiModules import Node
from Plugins import PluginManager


class leftPaneLayers:

    # The object that generates teh netowrk creation menu in the GUI
    # @param parent is the parent widget
    # @param colourScheme is the colourscheme of the widget
    # @param params are the parameters for the network [maxNeurons(int), learningRate(float), activationFunction(str), errorFunction(str)]
    # @param canvas is the tk.Canvas obj that the visual representation of the network should be drawn on

    def __init__(
        self,
        parent,
        colourScheme,
        params,
        canvas,
        ):
        self.labels = []
        self.menus = []
        self.parent = parent
        self.colourScheme = colourScheme
        self.maxNeurons = params[0]
        self.learningRate = params[1]
        self.activationFunc = params[2]
        self.activationFunc = params[3]
        self.buildBtn = Tk.Button(self.parent, text='Build',
                                  command=self.buildNetwork)
        self.errorLabel = Tk.Label(self.parent, text='invalid inputs',
                                   bg=self.colourScheme['background'],
                                   fg='red')
        self.canvas = canvas

    # Following function returns a list of layer labels
    # @param numOfLabels is an int that determines the number of layers

    def generateLayerLabels(self, numOfLayers):
        if isinstance(numOfLayers, int):
            labels = []
            for i in range(0, numOfLayers - 1):
                text = 'Layer ' + str(i) + ':'
                newLabel = Tk.Label(self.parent,
                                    bg=self.colourScheme['background'],
                                    text=text)
                labels.append(newLabel)

            # HyperParameters

            newLabel = Tk.Label(self.parent,
                                bg=self.colourScheme['background'],
                                text='ActivationFunc:')
            labels.append(newLabel)
            newLabel = Tk.Label(self.parent,
                                bg=self.colourScheme['background'],
                                text='Error Func:')
            labels.append(newLabel)
            newLabel = Tk.Label(self.parent,
                                bg=self.colourScheme['background'],
                                text='Learning Rate:')
            labels.append(newLabel)
            self.labels = labels
        else:
            raise TypeError('"numOfLayers" has to be an int.')

    # Following function returns a list of layer labels
    # @param numOfLabels is an int that determines the number of layers
    # maxNeurons is a class int that determines the number of options

    def generateLayerMenus(self, numOfLayers):
        if isinstance(numOfLayers, int):
            menus = []
            for i in range(0, numOfLayers - 1):
                newMenu = ttk.Combobox(self.parent, state='readonly',
                        values=list(range(1, self.maxNeurons)))
                newMenu.bind('<<ComboboxSelected>>', lambda x: \
                             self.parent.focus())
                menus.append(newMenu)

            # HyperParameters

            newMenu = ttk.Combobox(self.parent, state='readonly',
                                   values=PluginManager.getPluginNames('ActivationFunc'
                                   ))
            newMenu.bind('<<ComboboxSelected>>', lambda x: \
                         self.parent.focus())
            menus.append(newMenu)
            newMenu = ttk.Combobox(self.parent, state='readonly',
                                   values=PluginManager.getPluginNames('ErrorFunc'
                                   ))
            newMenu.bind('<<ComboboxSelected>>', lambda x: \
                         self.parent.focus())
            menus.append(newMenu)
            newMenu = Tk.Entry(self.parent)
            newMenu.insert(Tk.END, '0.1')
            menus.append(newMenu)
            self.menus = menus
        else:
            raise TypeError('"numOfLayers" has to be an int.')

    # Following function removes old layers, generates new layers, and renders them to parent
    # @param numOfLabels is an int that determines how many layers to show by default

    def renderLeftLayers(self, numOfLayers=2):

        # Remove old layers and button

        for i in range(0, len(self.labels)):
            self.labels[i].grid_remove()
            self.menus[i].grid_remove()
        self.buildBtn.grid_remove()
        self.errorLabel.grid_remove()

        # Generate new layers

        numOfLayers += 1
        self.generateLayerLabels(numOfLayers)
        self.generateLayerMenus(numOfLayers)

        # Render new layers

        row = 3
        for i in range(0, len(self.labels)):
            self.labels[i].grid(row=row, column=0, pady=5, sticky='e')
            self.menus[i].grid(row=row, column=1, pady=5, sticky='we')
            row += 1

        # Render "Build" button

        self.buildBtn.grid(row=row, column=1, pady=5, sticky='e')

    def buildNetwork(self):
        inputs = []
        for i in range(len(self.menus) - 3):
            if self.menus[i].get() == '':
                self.errorLabel.grid(row=len(self.labels) + 3,
                        column=1, pady=5, sticky='w')
                return
            inputs.append(int(self.menus[i].get()))

        # HyperParameters

        try:
            learnRate = float(self.menus[-1].get())
        except:
            self.errorLabel.grid(row=len(self.labels) + 3, column=1,
                                 pady=5, sticky='w')
            self.menus[-1].set('')
        activationFunc = self.menus[-3].get()
        errorFunc = self.menus[-2].get()

        self.errorLabel.grid_remove()
        Globals.NN = Network.Network(inputs, learnRate, activationFunc,
                errorFunc)

        Node.drawNodes(self.canvas)
