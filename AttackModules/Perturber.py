# -*- coding: utf-8 -*-

import Globals
import numpy as np


# Returns a 2D array of results and draws graphs
# [0] array of outputs
# [1] array of outputs
# ... ..... .. .......
# [255] array of outputs
#
# @param image is an ImageDisplay.image obj
# @param progress is a ttk.Progressbar obj of length 256
# @param window is a Tk.Toplevel obj (perturbingWindow from GuiModules.pertrubingWindow.py)
# @graphCollection is a list of ResultGraphing.Graph objs

def perturb(
    image,
    progress,
    window,
    graphCollection,
    ):

    # Exit if no pixel selected

    if image.currentPixel == None:
        raise RuntimeError('No current pixel selected')

    # Get current image

    inputs = image.getImgData()
    originalValue = inputs[image.currentPixelPos]

    # Create result array

    results = []
    for i in range(256):
        inputs[image.currentPixelPos] = i
        output = Globals.NN.forwardProp(inputs)
        results.append(output)
        progress['value'] += 1
        window.update()
    results = np.column_stack(results)

    # Plot graphs

    for (i, graph) in enumerate(graphCollection):
        graph.plotData(results[i], originalValue)

    # Close perturb window

    window.grab_release()
    window.destroy()

    return results


# Returns a 2D array of all possible perturbations and draws graphs for the pixel with the largest change in output
# Returns a 2D array of results and draws graphs
# [0] array of outputs
# [1] array of outputs
# ... ..... .. .......
# [255] array of outputs
#
# @param instance is the perterbingWindow obj
# @param image is an ImageDisplay.image obj
# @param progress is a ttk.Progressbar obj of length 256
# @param window is a Tk.Toplevel obj (perturbingWindow from GuiModules.pertrubingWindow.py)
# @graphCollection is a list of ResultGraphing.Graph objs

def perturbAll(
    instance,
    image,
    progress,
    window,
    graphCollection,
    ):

    # Get current image

    inputs = image.getImgData()

    # Create base result array

    originalOutput = Globals.NN.forwardProp(inputs)
    originalOutput = np.tile(originalOutput, (256, 1))
    mostSignificantResults = originalOutput
    mostSignificantPixel = 0
    largestDiff = 0

    # Create result array and compare against original

    for pixel in range(image.imgSize):
        results = []
        originalPixelVal = inputs[pixel]
        for i in range(256):
            inputs[pixel] = i
            output = Globals.NN.forwardProp(inputs)
            results.append(output)
            progress['value'] += 1
            window.update()

        # Restore pixel

        inputs[pixel] = originalPixelVal

        # Check if difference is largest

        temp = np.array([originalOutput, results])
        currentDiff = np.max(np.absolute(np.diff(temp, axis=0)))
        if currentDiff > largestDiff:
            largestDiff = currentDiff
            mostSignificantResults = results
            mostSignificantPixel = pixel

        # Check if stopped by user

        if instance.stop == True:
            return

    print ()
    print ()
    print ('Largest Difference: ', largestDiff)
    mostSignificantResults = np.column_stack(mostSignificantResults)

    # Plot graphs

    for (i, graph) in enumerate(graphCollection):
        graph.plotData(mostSignificantResults[i],
                       inputs[mostSignificantPixel])

    # Print most significant pixel position

    print ('Most Significant Pixel: ', mostSignificantPixel)
    print ('Most Significant Pixel Original Value: ',
           inputs[mostSignificantPixel])

    # Close perturb window

    window.grab_release()
    window.destroy()

    # Update current pixel

    image.click(image.pixel[image.imageNum][mostSignificantPixel],
                mostSignificantPixel)

    return mostSignificantResults


# Finds the largest distance from original for all pixels and draws a heatmap
# @param instance is a PerturbingWindow instance
# @param image is a ImageDisplay.image obj
# @param progress is the progressbar of instance
# @param window is the tk.toplevel obj of instance
# @param graphCollection is the array which contains graphs in the GUI

def getHeat(
    instance,
    image,
    progress,
    window,
    graphCollection,
    ):

    # Get current image

    inputs = image.getImgData()

    # Create base result array

    originalOutput = np.array(Globals.NN.forwardProp(inputs))

    # Get matrix of max distances

    maxDistMatrix = []

    for pixel in range(image.imgSize):
        originalPixelVal = inputs[pixel]
        for i in range(256):
            inputs[pixel] = i
            output = np.array(Globals.NN.forwardProp(inputs))

            # Update array of max distances for pixel

            if i == 0:
                maxDeltaOut = np.array(output)  # maxDeltaOut is an array of values furthest away from original (not distance)
            else:
                maxDeltaOut = np.where(np.abs(output - originalOutput)
                        > np.abs(maxDeltaOut - originalOutput), output,
                        maxDeltaOut)

            progress['value'] += 1
            window.update()

        # Build the matrix

        maxDeltaOut = maxDeltaOut - originalOutput
        maxDistMatrix.append(maxDeltaOut)

        # Restore pixel

        inputs[pixel] = originalPixelVal

        # Check if stop

        if instance.stop == True:
            return

    # Plot heatmaps

    maxDistMatrix = np.column_stack(maxDistMatrix)
    maxDistMatrix = maxDistMatrix.reshape(-1, image.imgSizeX,
            image.imgSizeY)
    for (i, graph) in enumerate(graphCollection):
        graph.plotMaxDistHeat(maxDistMatrix[i])

    # Close perturb window

    window.grab_release()
    window.destroy()

    return maxDistMatrix
