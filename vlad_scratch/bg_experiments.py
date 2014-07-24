from __future__ import division
import pprint
import sys
sys.path.append('../popoffka_scratch')

import numpy
import Image

import bkg


def save_as_image(arr, filename):
    Image.fromarray(arr.astype(numpy.uint8)).save(filename)


def reshape(arr, new_width):
    arr = arr.reshape(-1)
    arr = arr[:arr.size // new_width * new_width]
    return arr.reshape(arr.size // new_width, new_width)


if __name__ == '__main__':
    a = numpy.array(bkg.get_55x55_bits())

    print a
    print a.sum(), a.size

    #for w in range(7, 100):
    #    save_as_image(reshape(a, w) * 255, 'hz{}.png'.format(w))

