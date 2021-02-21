# -*- coding: utf-8 -*-

import tkinter as Tk
import tkinter.ttk as ttk
import configparser
from Data import DataManager
import Globals

# Get Configs

config = configparser.ConfigParser()
config.read('config.ini')
colourScheme = config['colourScheme']


class testingWindow:
    
    # Opens a window to test and display accuracy of the current network
    # @param dataPath is the string name of image file
    # @param labelPath is the string name of label file
    
    def __init__(self, dataPath, labelPath):
        self.stop = False

        dataPath = 'Data/Test Set Images/' + dataPath + '.gz'
        labelPath = 'Data/Test Set Labels/' + labelPath + '.gz'

        self.window = Tk.Toplevel()
        self.window.title('Testing')
        self.window.config(bg=colourScheme['background'])

        # window.overrideredirect(1)

        self.window.wm_geometry('400x120')
        self.window.resizable(False, False)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grab_set()

        sets = DataManager.getSetSize(dataPath)

        # Setup TreeView/Table

        self.table = ttk.Treeview(self.window)
        self.table['columns'] = ('Instances', 'Correct', 'Accuracy')
        self.table.column('#0', minwidth=30, stretch=Tk.NO)
        self.table.column('Instances', minwidth=60, stretch=Tk.NO)
        self.table.column('Correct', minwidth=120, stretch=Tk.NO)
        self.table.column('Accuracy', minwidth=60, stretch=Tk.NO)
        self.table.heading('#0', text='Digit', anchor=Tk.W)
        self.table.heading('Instances', text='Instances', anchor=Tk.W)
        self.table.heading('Correct', text='Correct Categorisaion',
                           anchor=Tk.W)
        self.table.heading('Accuracy', text='Accuracy', anchor=Tk.W)

        # Setup Progressbar

        self.progressLabel = Tk.Label(self.window,
                bg=colourScheme['background'], text='Progress:')
        self.progressLabel.grid(row=0, column=0, sticky='sw', padx=20,
                                pady=(10, 0))

        self.progressBar = ttk.Progressbar(self.window,
                orient='horizontal', maximum=sets, mode='determinate')
        self.progressBar.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky='we',
            padx=10,
            pady=10,
            )

        # Buttons

        btnFrame = Tk.Frame(self.window, bg=colourScheme['background'])
        btnFrame.grid(row=2, column=1, sticky='e', padx=10, pady=(0,
                      10))

        self.closeBtn = Tk.Button(btnFrame, text='Close',
                                  state='disabled', command=lambda : \
                                  self.closeFunc())
        self.stopBtn = Tk.Button(btnFrame, text='Stop',
                                 command=lambda : self.stopFunc())

        self.stopBtn.grid(row=0, column=0, sticky='w')
        self.closeBtn.grid(row=0, column=1, padx=(10, 0), sticky='e')

        # Check if there is a network to test

        if Globals.NN.structure == []:
            self.progressLabel['text'] = 'Progress: Network Missing'
            self.progressBar['value'] = sets
            self.stopFunc()
            return

        # Run Testing and display grid

        Globals.NN.test(dataPath, labelPath, self)
        self.stopFunc()
        self.progressLabel.destroy()
        self.progressBar.destroy()
        self.table.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky='nswe',
            padx=10,
            pady=10,
            )
        self.window.wm_geometry('700x350')

        return

    def stopFunc(self):
        self.stop = True
        self.stopBtn.config(state='disabled')
        self.closeBtn.config(state='normal')

    def closeFunc(self):
        self.window.grab_release()
        self.window.destroy()
