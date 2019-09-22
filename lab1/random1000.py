#!/usr/bin/env python3

# Generate 1000 random numbers with exponential distribution and calculate mean/variance.

import math
import statistics
from random import random

nums = []
lam = 75

for i in range(1000):
    randnum = -(1.0/lam)*math.log(1 - random())
    nums.append(randnum)

avg = statistics.mean(nums)
var = statistics.pvariance(nums)

print(avg, var)
