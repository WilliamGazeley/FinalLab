# -*- coding: utf-8 -*-
# Import Tkinter modules

import tkinter as Tk
from tkinter import ttk
import configparser
from tkinter.filedialog import asksaveasfilename

# Import GUI Modules

from GuiModules.LeftPaneLayers import leftPaneLayers
from GuiModules import Node
from GuiModules.TrainingWindow import trainingWindow
from GuiModules.TestingWindow import testingWindow
from GuiModules.PerturbingWindow import perturbingWindow
from GuiModules import ImageDisplay
from GuiModules.ResultGraphing import Graph

# Import backend modules

import Globals
from Data import DataManager
from Models import ModelManager
import pickle
import os


# Starts the GUI. Can only be called from plab root directory

def run():

    # Get Configs

    config = configparser.ConfigParser()
    config.read('config.ini')
    colourScheme = config['colourScheme']
    neuralNet = config['neuralNet']
    maxLayers = list(range(2, int(neuralNet['maxLayers']) + 1))
    defaultData = config['defaults']['dataSets'].split(',\n')

    # Setup Layout

    Root = Tk.Tk()
    Root.title('Neural Network Experiment')
    Root.configure(bg=colourScheme['background'])
    Root.minsize(1300, 800)
    Root.geometry('1300x800+0+0')
    Root.grid_columnconfigure(1, weight=1)
    Root.grid_rowconfigure(0, weight=1)

    # Left Pane ===============================================

    LeftPane = Tk.Frame(Root, width=600, height=800,
                        bg=colourScheme['background'])
    LeftPane.grid(row=0, column=0, padx=(20, 10), pady=20, sticky='ns')

    # Get Network Display Canvas Ready

    RightPane = Tk.Frame(Root, bg=colourScheme['background'])
    VisRepFrame = Tk.Frame(RightPane)
    VisRepFrame.grid_columnconfigure(0, weight=1)
    VisRepFrame.grid(row=2, columnspan=2, pady=10, sticky='nwe')

    VisRep = Tk.Canvas(VisRepFrame, bg=colourScheme['nodeBkGd'],
                       cursor='hand2')
    VisRep.grid(row=0, column=0, sticky='we')

    VisRepHbar = Tk.Scrollbar(VisRepFrame, orient='horizontal',
                              command=VisRep.xview)
    VisRepHbar.grid(row=1, column=0, columnspan=2, sticky='nswe')
    VisRepVbar = Tk.Scrollbar(VisRepFrame, orient='vertical',
                              command=VisRep.yview)
    VisRepVbar.grid(row=0, column=1, sticky='nswe')

    VisRep.config(xscrollcommand=VisRepHbar.set,
                  yscrollcommand=VisRepVbar.set,
                  scrollregion=VisRep.bbox('all'))

    # Import the default network

    importModel(defaultData[4], VisRep)

    # Network construction pane

    defaultParams = [int(neuralNet['maxNeurons']),
                     float(neuralNet['learningRate']),
                     neuralNet['activationFunc'], neuralNet['errorFunc'
                     ]]
    layerSetup = leftPaneLayers(LeftPane, colourScheme, defaultParams,
                                VisRep)

    NoOfLayers_Label = Tk.Label(LeftPane, bg=colourScheme['background'
                                ], text='Number of Layers:')
    NoOfLayers_Label.grid(row=0, column=0, columnspan=2, sticky='w')
    NoOfLayers_Menu = ttk.Combobox(LeftPane, state='readonly',
                                   values=maxLayers)
    NoOfLayers_Menu.set(2)
    NoOfLayers_Menu.grid(row=1, column=0, columnspan=2, sticky='we')
    NoOfLayers_Menu.bind('<<ComboboxSelected>>', lambda x: \
                         [layerSetup.renderLeftLayers(int(NoOfLayers_Menu.get())),
                         LeftPane.focus()])

    NumberOfNeurons_Label = Tk.Label(LeftPane,
            bg=colourScheme['background'], text='Number of Neurons:')
    NumberOfNeurons_Label.grid(row=2, column=1, sticky='w', pady=(20,
                               0))

    layerSetup.renderLeftLayers()

    # RightPane ===============================================

    RightPane.grid_columnconfigure(1, weight=1)
    RightPane.grid_rowconfigure(15, weight=1)
    RightPane.grid(row=0, column=1, padx=(0, 20), pady=20, sticky='nswe'
                   )

    Node.drawNodes(VisRep)
    VisRep.bind('<Button-1>', lambda x: Node.click(VisRep))

    # Result Graphs (Canvas is scrollable) --------------------

    ResultFrame = Tk.Frame(RightPane, bg='white')
    ResultFrame.grid_columnconfigure(0, weight=1)
    ResultFrame.grid_rowconfigure(0, weight=1)
    ResultFrame.grid(
        row=2,
        column=2,
        rowspan=14,
        padx=(10, 0),
        pady=(10, 0),
        sticky='nswe',
        )

    ResultScrollable = Tk.Canvas(ResultFrame)
    InternalScrollableFrame = Tk.Frame(ResultScrollable)
    ResultScrollable.create_window(0, 0,
                                   window=InternalScrollableFrame,
                                   anchor='nw')
    ResultScrollable.grid(row=0, column=0, padx=(5, 0), sticky='nswe')

    graphCollection = []
    for i in range(10):
        graphCollection.append(Graph(InternalScrollableFrame, i))

    ResultFrameVbar = Tk.Scrollbar(ResultFrame, orient='vertical',
                                   command=ResultScrollable.yview)
    ResultFrameVbar.grid(row=0, column=1, sticky='nswe')

    ResultScrollable.config(yscrollcommand=ResultFrameVbar.set,
                            scrollregion=ResultScrollable.bbox('all'))

    # AttackFrame ---------------------------------------------

    AtkFrame = Tk.Frame(RightPane, bg=colourScheme['background'])
    AtkFrame.grid_columnconfigure(0, weight=1, minsize=235)
    AtkFrame.grid(row=3, column=1, rowspan=13, padx=(10, 0),
                  sticky='nswe')

    # Create and show image

    ImgCanv = ImageDisplay.image(AtkFrame, 'Data/Attack Set Images/'
                                 + defaultData[5] + '.gz')
    ImgCanv.renderImage()

    # Buttons

    ImgBtnFrame = Tk.Frame(AtkFrame)
    PrevImageBtn = Tk.Button(ImgBtnFrame, text='<', width=3,
                             command=ImgCanv.prevImage)
    PerturbBtn = Tk.Button(ImgBtnFrame, text='Perturb', width=23,
                           command=lambda : perturbingWindow(ImgCanv,
                           graphCollection))
    NextImageBtn = Tk.Button(ImgBtnFrame, text='>', width=3,
                             command=ImgCanv.nextImage)
    ImgBtnFrame.grid(row=1, column=0, pady=10)
    PrevImageBtn.grid(row=0, column=0)
    PerturbBtn.grid(row=0, column=1)
    NextImageBtn.grid(row=0, column=2)
    PerturbAllBtn = Tk.Button(ImgBtnFrame, text='Perturb All Pixels',
                              command=lambda : \
                              perturbingWindow(ImgCanv,
                              graphCollection, findMax=True))
    PerturbAllBtn.grid(row=1, column=0, columnspan=3, sticky='we')
    PlotHeatBtn = Tk.Button(ImgBtnFrame, text='Plot Heatmaps',
                            command=lambda : perturbingWindow(ImgCanv,
                            graphCollection, findMax=True,
                            plotHeat=True))
    PlotHeatBtn.grid(row=2, column=0, columnspan=3, sticky='we')

    # Perturb data Comboboxes

    AtkPickerFrame = Tk.Frame(AtkFrame, bg=colourScheme['background'])
    AtkPickerFrame.grid(column=1, row=0, columnspan=4, padx=10,
                        sticky='nw')

    AtkImageLabel = Tk.Label(AtkPickerFrame,
                             bg=colourScheme['background'],
                             text='Images to be Perturbed: ')
    AtkImageCombo = ttk.Combobox(AtkPickerFrame, width=25,
                                 state='readonly',
                                 values=DataManager.getDataName('attack images'
                                 ))
    AtkImageCombo.bind('<<ComboboxSelected>>', lambda x: \
                       RightPane.focus())
    AtkImageCombo.set(defaultData[5])
    AtkImageLabel.grid(column=1, row=0, sticky='w')
    AtkImageCombo.grid(column=1, row=1, sticky='w')

    ImportAtkSetBtn = Tk.Button(AtkPickerFrame,
                                text='Import Attack Images',
                                command=lambda : \
                                importAttackSet(AtkImageCombo.get(),
                                ImgCanv))
    ImportAtkSetBtn.grid(column=1, row=4, pady=(10, 0), sticky='we')

    # Data Pickers --------------------------------------------

    TrainImageLabel = Tk.Label(RightPane, bg=colourScheme['background'
                               ], text='Training Images:')
    TrainImageCombo = ttk.Combobox(RightPane, width=25, state='readonly'
                                   ,
                                   values=DataManager.getDataName('train images'
                                   ))
    TrainImageCombo.bind('<<ComboboxSelected>>', lambda x: \
                         RightPane.focus())
    TrainImageCombo.set(defaultData[0])
    TrainImageLabel.grid(column=0, row=3, sticky='w')
    TrainImageCombo.grid(column=0, row=4, sticky='w')

    TrainLabelsLabel = Tk.Label(RightPane, bg=colourScheme['background'
                                ], text='Training Labels:')
    TrainLabelsCombo = ttk.Combobox(RightPane, width=25,
                                    state='readonly',
                                    values=DataManager.getDataName('train labels'
                                    ))
    TrainLabelsCombo.bind('<<ComboboxSelected>>', lambda x: \
                          RightPane.focus())
    TrainLabelsCombo.set(defaultData[1])
    TrainLabelsLabel.grid(column=0, row=5, sticky='w')
    TrainLabelsCombo.grid(column=0, row=6, sticky='w')

    TestImageLabel = Tk.Label(RightPane, bg=colourScheme['background'],
                              text='Test Images:')
    TestImageCombo = ttk.Combobox(RightPane, width=25, state='readonly'
                                  ,
                                  values=DataManager.getDataName('test images'
                                  ))
    TestImageCombo.bind('<<ComboboxSelected>>', lambda x: \
                        RightPane.focus())
    TestImageCombo.set(defaultData[2])
    TestImageLabel.grid(column=0, row=7, sticky='w')
    TestImageCombo.grid(column=0, row=8, sticky='w')

    TestLabelsLabel = Tk.Label(RightPane, bg=colourScheme['background'
                               ], text='Test Labels:')
    TestLabelsCombo = ttk.Combobox(RightPane, width=25, state='readonly'
                                   ,
                                   values=DataManager.getDataName('test labels'
                                   ))
    TestLabelsCombo.bind('<<ComboboxSelected>>', lambda x: \
                         RightPane.focus())
    TestLabelsCombo.set(defaultData[3])
    TestLabelsLabel.grid(column=0, row=9, sticky='w')
    TestLabelsCombo.grid(column=0, row=10, sticky='w')

    # Buttons -----------------------------------------------------

    opBtnFrame = Tk.Frame(RightPane, bg=colourScheme['background'])
    opBtnFrame.grid_columnconfigure(0, weight=1)
    opBtnFrame.grid_columnconfigure(1, weight=1)
    opBtnFrame.grid(row=11, pady=(10, 0), sticky='we')

    TrainBtn = Tk.Button(opBtnFrame, text='Train', command=lambda : \
                         trainingWindow(TrainImageCombo.get(),
                         TrainLabelsCombo.get()))
    TrainBtn.grid(row=0, column=0, sticky='we')

    TestBtn = Tk.Button(opBtnFrame, text='Test', command=lambda : \
                        testingWindow(TestImageCombo.get(),
                        TestLabelsCombo.get()))
    TestBtn.grid(row=0, column=1, padx=(5, 0), sticky='we')

    ExportBtn = Tk.Button(opBtnFrame, text='Export Model',
                          command=lambda : exportFunc())
    ExportBtn.grid(row=1, column=0, columnspan=3, pady=(5, 0),
                   sticky='we')

    # Import Model -------------------------------------------------

    ImportLabel = Tk.Label(RightPane, bg=colourScheme['background'],
                           text='Pretrained Model:')
    ImportLabel.grid(column=0, row=12, pady=(10, 0), sticky='w')

    ImportCombo = ttk.Combobox(RightPane, width=25, state='readonly',
                               values=ModelManager.getModelNames(),
                               postcommand=lambda : \
                               updateImportCombo(ImportCombo))
    ImportCombo.bind('<<ComboboxSelected>>', lambda x: \
                     RightPane.focus())
    ImportCombo.set(defaultData[4])
    ImportCombo.grid(column=0, row=13, sticky='w')

    ImportBtn = Tk.Button(RightPane, text='Import Model',
                          command=lambda : \
                          importModel(ImportCombo.get(), VisRep))
    ImportBtn.grid(column=0, row=14, pady=(10, 0), sticky='we')

    # =============================================================

    Tk.mainloop()


# Displays the os file browser and saves the current model at that location and filename

def exportFunc():
    path = asksaveasfilename(initialdir=os.getcwd() + '\\Models',
                             initialfile='MyTrainedModel',
                             defaultextension='.pickle',
                             filetypes=[('Pickle', '*.pickle')],
                             title='Export')
    Globals.NN.export(path)


# Used to update ImportCombo when new model is exported
# @param importCombo is a ttk.combobox obj

def updateImportCombo(importCombo):
    importCombo['values'] = ModelManager.getModelNames()
    return


# Unpickles a file containing a pretrained model and returns it
# @param modelName is the name of the model found in the Models folder
# @param canvas is the visual representation of network in Gui

def importModel(modelName, canvas):
    if modelName == '':
        return

    path = 'Models/' + modelName + '.pickle'
    file = open(path, 'rb')
    Globals.NN = pickle.load(file)
    file.close()

    Node.drawNodes(canvas)
    return


# Displays and imports the new attack set
# @param imgsPath is the name of the image file (string)
# @param ImgCanv is the ImageDisplay.image obj

def importAttackSet(imgsPath, ImgCanv):
    ImgCanv.unrenderImage()
    ImgCanv.newImg('Data/Attack Set Images/' + imgsPath + '.gz')
    ImgCanv.renderImage()
