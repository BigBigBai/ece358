# Util functions for Lab 1

import math
from random import random


# Returns an exponential random variable
def get_random_variable(mean):
    return -mean*math.log(1-random())
