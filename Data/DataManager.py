# -*- coding: utf-8 -*-

import os
import gzip
import numpy as np


# Returns an array of file names for the given data type
# @param dataType is a string to determine which folder to use

def getDataName(dataType):

    if not isinstance(dataType, str):
        raise ValueError('dataType must be string.')

    names = []

    if dataType == 'test images':
        folder = os.listdir('Data/Test Set Images')
        for data in folder:
            names.append(data[:-3])
    elif dataType == 'test labels':

        folder = os.listdir('Data/Test Set Labels')
        for data in folder:
            names.append(data[:-3])
    elif dataType == 'train images':

        folder = os.listdir('Data/Train Set Images')
        for data in folder:
            names.append(data[:-3])
    elif dataType == 'train labels':

        folder = os.listdir('Data/Train Set Labels')
        for data in folder:
            names.append(data[:-3])
    elif dataType == 'attack images':

        folder = os.listdir('Data/Attack Set Images')
        for data in folder:
            names.append(data[:-3])
    elif dataType == 'attack labels':

        folder = os.listdir('Data/Attack Set Labels')
        for data in folder:
            names.append(data[:-3])
    else:

        raise ValueError('dataType is invalid.')

    return names


# Returns a the size of the data set as an int
# @param path is the full path string to a data set

def getSetSize(path):
    data = gzip.open(path, 'r')
    data.read(4)
    setSize = int.from_bytes(data.read(4), byteorder='big')
    data.close()
    return setSize


# Returns the size (num of pixels) per image
# @param path is the full path string
# @param split is a bool that determines if the XY dims should be returns individually
# if split, [0] is Y axis and [1] is X axis

def getImgSize(path, split=False):
    data = gzip.open(path, 'r')
    data.read(8)

    if split == False:
        size = int.from_bytes(data.read(4), byteorder='big') \
            * int.from_bytes(data.read(4), byteorder='big')
    else:
        size = [int.from_bytes(data.read(4), byteorder='big'),
                int.from_bytes(data.read(4), byteorder='big')]
    data.close()

    return size


# Returns an image from a data set in the form of a np array
# @param path is the path strimg to the data set
# @param imgNum is the int image number in the file (0 is the first image)

def getImage(path, imgNum=0):
    imgSize = getImgSize(path)
    data = gzip.open(path, 'r')

    # Skip to wanted image

    data.seek(16 + imgSize * imgNum)

    # Get image

    buffer = data.read(imgSize)
    image = np.frombuffer(buffer, dtype=np.uint8)

    return image
