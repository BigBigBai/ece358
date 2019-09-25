# Util functions for Lab 1

import csv
import math
from random import random


# Returns an exponential random variable
def get_random_variable(mean):
    return -mean*math.log(1-random())


# Writes the results to the corresponding CSV file.
def write_to_csv(file, headers, data):
    with open(file, mode='w', newline='') as output_file:
        output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        output_writer.writerow(headers)
        for result in data:
            output_writer.writerow(result)

    print('Results written to {}'.format(file))