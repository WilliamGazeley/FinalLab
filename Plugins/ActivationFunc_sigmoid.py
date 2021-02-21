# -*- coding: utf-8 -*-

import math


def Func(x):
    if x < 0:
        return 1 - 1 / (1 + math.exp(x))
    return 1 / (1 + math.exp(-x))


def FuncPrime(x):
    return x * (1 - x)
