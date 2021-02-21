# -*- coding: utf-8 -*-

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
import numpy as np

matplotlib.rcParams.update({'font.size': 5})


class Graph:

    # Draws and return a placeholder for a graph
    # @param parent is the Tk.Frame parent obj
    # @param destDigit is the (string) destination digit for the graph

    def __init__(self, parent, destDigit):
        
        # Turn off each graph opening a new window
        # (an issue when running from spyder)
        
        plt.ioff()

        # Initialise graph

        self.onePixTitle = \
            'Certainty that image is digit: {}'.format(destDigit)
        self.heatTitle = \
            'Max one-pixel distances to digit {}'.format(destDigit)
        self.fig = plt.figure(figsize=(4, 4))
        self.plot = self.fig.add_subplot()
        self.plot.set_title(self.onePixTitle, fontsize=14)
        self.plot.set_ylim(top=1)
        self.plot.set_xlim(right=255)
        self.plot.set_ylabel('Certainty', fontsize=10)
        self.plot.set_xlabel('Pixel Value', fontsize=10)
        self.colorbar = None

        # Draw

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().grid(column=0)
        self.canvas.draw()

        return

    # Clears the current plot

    def clear(self):
        self.plot.remove()
        self.plot = self.fig.add_subplot()
        self.plot.set_title(self.onePixTitle, fontsize=14)
        if self.colorbar != None:
            self.colorbar.remove()
            self.colorbar = None

        self.canvas.draw()

    # Draws a plot of certainty against perturbation of a certain pixel
    # @param x is a np.array of results from perturbation
    # @param original is the (int) original gamma value of the selected pixel

    def plotData(self, y, originalGamma):

        # Clear previous plot

        self.clear()

        # Plot new results

        x = np.arange(0, 256)
        maxY = np.amax(y)
        minY = np.amin(y)
        self.plot.set_title(self.onePixTitle, fontsize=14)
        self.plot.set_ylim(top=1)
        self.plot.set_xlim(right=255)
        self.plot.set_ylabel('Certainty', fontsize=10)
        self.plot.set_xlabel('Pixel Value', fontsize=10)
        self.plot.plot(x, y, color='blue',
                       label='Max Certainty: {:.2f}\nMin Certainty: {:.2f}'.format(maxY,
                       minY))
        self.plot.axvline(originalGamma,
                          label='Original Value: {}'.format(str(originalGamma)),
                          color='grey', ls='--')

        self.plot.legend(prop={'size': 6})

        # Draw Graph

        self.canvas.draw()

        return

    # @param maxDistMatrix is a 2d array of floats
    # @param scale determines if color range should be scaled to match values

    def plotMaxDistHeat(self, maxDistMatrix, scale=True):

        # Clear previous plot

        self.clear()

        # Check if maxDistMatrix is all neg or all pos

        positive = np.any(maxDistMatrix > 0)
        negative = np.any(maxDistMatrix < 0)

        if positive == True and negative == False:
            cmap = 'Reds'
        elif positive == False and negative == True:
            cmap = 'Blues_r'
        else:
            cmap = 'coolwarm'

        # Plot new results

        self.plot.set_title(self.heatTitle, fontsize=10)

        if scale == True:
            v = np.amax(np.abs(maxDistMatrix))
            self.colorbar = \
                self.fig.colorbar(self.plot.imshow(maxDistMatrix,
                                  cmap=cmap, vmax=v, vmin=-v),
                                  shrink=0.7)
        else:
            self.colorbar = \
                self.fig.colorbar(self.plot.imshow(maxDistMatrix,
                                  cmap=cmap, vmin=-1, vmax=1),
                                  shrink=0.7)

        # Draw Graph

        self.canvas.draw()
