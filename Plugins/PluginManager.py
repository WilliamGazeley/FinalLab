# -*- coding: utf-8 -*-

import os
import csv


# Returns a dictionary of modules for each plugin matching the plugin type
# @param pluginType is a string

def importPlugins(pluginType):
    output = {}
    plugins = os.listdir('Plugins')
    headerlen = len(pluginType) + 9

    # Validate pluginType

    checkTypeValid(pluginType)

    # import only plugins matching pluginType

    for i in range(0, len(plugins)):
        if plugins[i].startswith(pluginType):
            toimport = 'Plugins.' + (plugins[i])[:-3]
            output[toimport[headerlen:]] = __import__(toimport,
                    fromlist=[None])

    return output


# Returns a list of the names of plugins of a given type
# @param pluginType is a string

def getPluginNames(pluginType):
    plugins = os.listdir('Plugins')
    headerlen = len(pluginType) + 1
    names = []

    # get names only of plugins matching pluginType

    for i in range(0, len(plugins)):
        if plugins[i].startswith(pluginType):
            names.append((plugins[i])[headerlen:-3])
    return names


# Auxillary function that returns True if plugin type is valid, else raise error
# @param pluginType is a string

def checkTypeValid(pluginType):
    with open('Plugins/PluginTypes.csv') as validTypes:
        reader = csv.reader(validTypes)
        for validType in reader:
            if validType[0] == pluginType:
                return True
        raise ValueError('Plugin Type %s does not exist' % pluginType)
