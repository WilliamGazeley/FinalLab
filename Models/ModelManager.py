# -*- coding: utf-8 -*-

import os


# Returns an array of model names in the Models folder

def getModelNames():

    names = []

    folder = os.listdir('Models')
    for model in folder:
        names.append(model[:-7])

    names.remove('__py')
    names.remove('ModelMan')

    return names
