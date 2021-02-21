# -*- coding: utf-8 -*-

import tkinter as Tk
from tkinter import ttk
from Plugins import PluginManager
import configparser
import Globals

actFuncList = PluginManager.getPluginNames('ActivationFunc')
errFuncList = PluginManager.getPluginNames('ErrorFunc')

# Get Configs

config = configparser.ConfigParser()
config.read('config.ini')
colourScheme = config['colourScheme']
fonts = config['fonts']
neuralNet = config['neuralNet']
maxLayers = list(range(2, int(neuralNet['maxLayers']) + 1))


# Opens a window containing the variables of a given neuron
# @param neuron is the neuron obj

def newWindow(neuron):
    window = Tk.Toplevel()
    window.grab_current()
    window.title('Neuron')
    window.config(bg=colourScheme['background'])
    window.attributes('-topmost', 'true')
    window.maxsize(width=0, height=600)
    window.resizable(False, False)
    window.grid_rowconfigure(1, weight=1)
    window.grid_columnconfigure(1, weight=1)

    # Render name

    neuronName = Tk.Label(window, bg=colourScheme['background'],
                          text='Neuron: ' + str(neuron.name),
                          font=(fonts['header.style'],
                          int(fonts['header.px'])))
    neuronName.grid(columnspan=2, sticky='w', padx=10, pady=10)

    # Render leftPane

    leftPane = Tk.Frame(window, bg=colourScheme['background'])
    leftPane.grid(column=0, row=1, padx=10, sticky='n')

    actLabel = Tk.Label(leftPane, text='Activation:',
                        bg=colourScheme['background'])
    actLabel.grid(row=0, sticky='w')
    actEntry = Tk.Entry(leftPane)
    actEntry.insert(0, str(neuron.a))
    actEntry.config(state='readonly')
    actEntry.grid(row=1, sticky='we', pady=(0, 10))

    biasLabel = Tk.Label(leftPane, text='Bias:',
                         bg=colourScheme['background'])
    biasLabel.grid(row=2, sticky='w')
    biasEntry = Tk.Entry(leftPane)
    biasEntry.insert(0, str(neuron.b))
    biasEntry.grid(row=3, sticky='we', pady=(0, 10))

    actFuncLabel = Tk.Label(leftPane, text='Activation Function:',
                            bg=colourScheme['background'])
    actFuncLabel.grid(row=4, sticky='w')
    actFuncEntry = ttk.Combobox(leftPane, state='readonly',
                                values=actFuncList)
    actFuncEntry.bind('<<ComboboxSelected>>', lambda x: \
                      leftPane.focus())
    actFuncEntry.set(neuron.actFunc)
    actFuncEntry.grid(row=5, sticky='we', pady=(0, 5))

    errFuncLabel = Tk.Label(leftPane, text='Error Function:',
                            bg=colourScheme['background'])
    errFuncLabel.grid(row=6, sticky='w')
    errFuncEntry = ttk.Combobox(leftPane, state='readonly',
                                values=errFuncList)
    errFuncEntry.bind('<<ComboboxSelected>>', lambda x: \
                      leftPane.focus())
    errFuncEntry.set(neuron.errFunc)
    errFuncEntry.grid(row=7, sticky='we')

    learningRateLabel = Tk.Label(leftPane, text='Learning Rate:',
                                 bg=colourScheme['background'])
    learningRateLabel.grid(row=8, sticky='w')
    learningRateEntry = Tk.Entry(leftPane)
    learningRateEntry.bind('<<ComboboxSelected>>', lambda x: \
                           leftPane.focus())
    learningRateEntry.insert(0, str(neuron.R))
    learningRateEntry.grid(row=9, sticky='we')

    # Right pane

    rightPane = Tk.Frame(window, width=200, height=500,
                         bg=colourScheme['background'])
    rightPane.grid_propagate(False)
    rightPane.grid_rowconfigure(0, weight=1)
    rightPane.grid_columnconfigure(0, weight=1)
    rightPane.grid(column=1, row=1, padx=(0, 10), sticky='nswe')
    scrollableCanvas = Tk.Canvas(rightPane, bg=colourScheme['background'
                                 ], highlightthickness=0)
    scrollableCanvas.grid(row=0, column=0, sticky='nswe')
    scrollableFrame = Tk.Frame(scrollableCanvas,
                               bg=colourScheme['background'])
    scrollableFrame.grid_columnconfigure(0, weight=1)
    scrollableFrame.grid(sticky='we')

    row = 0
    weightEntries = []
    for i in range(len(neuron.w)):
        entryLabel = Tk.Label(scrollableFrame,
                              bg=colourScheme['background'],
                              text='Weight {}:'.format(i))
        entryLabel.grid(row=row, sticky='w')
        row += 1
        newEntry = Tk.Entry(scrollableFrame)
        weightEntries.append(newEntry)
        newEntry.insert(0, str(neuron.w[i]))
        newEntry.grid(row=row, sticky='we', pady=(0, 5))
        row += 1

    window.update()

    scrollableCanvas.create_window((0, 0), window=scrollableFrame,
                                   anchor='nw', width=200)

    vScrollbar = Tk.Scrollbar(rightPane, orient='vertical',
                              command=scrollableCanvas.yview)
    vScrollbar.grid(row=0, column=1, sticky='nswe')
    scrollableCanvas.config(yscrollcommand=vScrollbar.set,
                            scrollregion=scrollableCanvas.bbox('all'))

    # Buttons

    btnWrapper = Tk.Frame(window, bg=colourScheme['background'])
    btnWrapper.grid(row=2, columnspan=2, sticky='e', padx=10, pady=10)
    cancelButton = Tk.Button(btnWrapper, text='Cancel',
                             command=window.destroy)
    cancelButton.pack(side='right', padx=5)
    doneButton = Tk.Button(btnWrapper, text='Done', command=lambda : \
                           [setNode(
            neuron,
            biasEntry,
            actFuncEntry,
            errFuncEntry,
            weightEntries,
            learningRateEntry,
            ), window.destroy()])
    doneButton.pack(side='right', padx=5)


# Following function changes the variables of a given neuron. Aux func of the
# Node window, called when 'Done' btn clicked
# @param neuron is a neuron obj
# @param bias, actFunc, errFunc are Tk.Entry objs
# @param weightEntries is an array of Tk.Entry objs

def setNode(
    neuron,
    bias,
    actFunc,
    errFunc,
    weightEntries,
    learnRate,
    ):
    neuron.b = float(bias.get())
    neuron.actFunc = str(actFunc.get())
    neuron.errFunc = str(errFunc.get())
    neuron.R = float(learnRate.get())
    for i in range(0, len(weightEntries)):
        neuron.w[i] = float(weightEntries[i].get())

# Draws network on canvas
# @param canvas is the tk.Canvas object to draw the network on

def drawNodes(canvas):
    canvas.delete('all')

    # Draw Lines

    x = 30
    layerNum = 0
    for i in range(0, len(Globals.NN.structure) - 1):
        y = -10
        for j in range(0, Globals.NN.structure[i]):
            y += 40
            y2 = 30
            for k in range(0, Globals.NN.structure[i + 1]):
                canvas.create_line(x, y, x + 120, y2)
                y2 += 40
        x += 120

    # Draw nodes

    x = 30
    nodeNum = 1
    layerNum = 0
    for Layer in Globals.NN.Network:
        y = 30
        for Neuron in Layer.Layer:
            canvas.create_oval(
                x - 7,
                y + 7,
                x + 7,
                y - 7,
                fill=colourScheme['nodeFill'],
                tags=[nodeNum, layerNum],
                )
            nodeNum += 1
            y += 40
        layerNum += 1
        x += 120

    canvas.config(scrollregion=canvas.bbox('all'))

# Opens neuron window when corresponding to the neuron that was clicked on
# canvas
# @param canvas is the tk.Canvas obj that contains the network representation

def click(canvas):
    if canvas.find_withtag('current'):
        name = int(canvas.gettags(canvas.find_withtag('current'))[0])
        for i in range(0, len(Globals.NN.structure)):
            if name - Globals.NN.structure[i] <= 0:
                layer = i
                break
            name -= Globals.NN.structure[i]

        neuron = Globals.NN.Network[layer].Layer[name - 1]
        newWindow(neuron)
