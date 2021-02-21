# -*- coding: utf-8 -*-

import configparser
import tkinter as Tk
from tkinter import ttk
from AttackModules.Perturber import perturb, perturbAll, getHeat
import threading

# Get Configs

config = configparser.ConfigParser()
config.read('config.ini')
colourScheme = config['colourScheme']

lock = threading.Lock()
finished = False


class perturbingWindow:

    # @param image is an np.array of ints to be perturbed
    # @param graphCollection is a list of ResultGraphing.Graph objs
    # @param All is a boolean that determines if the max output change should be found
    # @param plotHeat is a boolean that determines if the max distances from original output should be plotted on a heatmap

    def __init__(
        self,
        image,
        graphCollection,
        findMax=False,
        plotHeat=False,
        ):

        # Exit if no pixel selected

        if image.currentPixel == None and findMax == False:
            return

        self.stop = False

        self.graphCollection = graphCollection

        self.window = Tk.Toplevel()
        self.window.title('Perturbing')
        self.window.config(bg=colourScheme['background'])

        # window.overrideredirect(1)

        self.window.wm_geometry('400x80')
        self.window.resizable(False, False)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grab_set()

        # Buttons

        btnFrame = Tk.Frame(self.window, bg=colourScheme['background'])
        btnFrame.grid(row=1, column=0, sticky='e', padx=10, pady=(0,
                      10))

        closeBtn = Tk.Button(btnFrame, text='Close', state='disabled',
                             command=lambda : \
                             self.closeFunc(self.window))
        stopBtn = Tk.Button(btnFrame, text='Stop', command=lambda : \
                            self.stopFunc(stopBtn, closeBtn))

        stopBtn.grid(row=0, column=0, sticky='w')
        closeBtn.grid(row=0, column=1, padx=(10, 0), sticky='e')

        if findMax == False:
            perturbProgress = ttk.Progressbar(self.window,
                    orient='horizontal', maximum=256, mode='determinate'
                    )
            perturbProgress.grid(row=0, sticky='we', padx=10, pady=10)

            # Start perturbation

            perturb(image, perturbProgress, self.window,
                    graphCollection)
        elif findMax == True:

            perturbProgress = ttk.Progressbar(self.window,
                    orient='horizontal', maximum=256 * image.imgSize,
                    mode='determinate')
            perturbProgress.grid(row=0, sticky='we', padx=10, pady=10)

            # Start perturbation

            if plotHeat == False:
                perturbAll(self, image, perturbProgress, self.window,
                           graphCollection)
            elif plotHeat == True:
                getHeat(self, image, perturbProgress, self.window,
                        graphCollection)
        else:

            raise ValueError('"All" must be Boolean')

        return

    def stopFunc(self, stopBtn, closeBtn):
        self.stop = True
        stopBtn.config(state='disabled')
        closeBtn.config(state='normal')

    def closeFunc(self, window):
        window.grab_release()
        window.destroy()
