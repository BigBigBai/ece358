# Util functions for Lab 1

import csv
import math
from random import random, randint

from . import constants as c


# Returns an exponential random variable
def get_random_variable(mean):
    return -mean*math.log(1-random())


# Calculates exponential backoff given number of collisions
def get_exponential_backoff(collisions):
    return randint(0, 2**collisions) * 512 / c.R
