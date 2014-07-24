#!/usr/bin/env python2
import os
try:
    from PIL import Image
except:
    print 'sudo pip2 install pillow'

reverse = lambda l: l[::-1]

def get_53x53_bits(im=None):
    im = im or Image.open('bkg.png')
    res = []
    for y in range(53):
        line = []
        realY = 1 + 10 * y
        for x in range(53):
            realX = 1 + 10 * x
            r, _, _ = im.getpixel((realX, realY))
            r /= 255
            line.append(r)
        res.append(line)
    return res

def get_55x55_bits(im=None):
    im = im or Image.open(os.path.join(os.path.dirname(__file__), 'bkg.png'))
    res = []
    for y in range(55):
        line = []
        if y == 0: realY = 0
        else:      realY = 1 + 10 * (y - 1)

        for x in range(55):
            if x == 0: realX = 0
            else:      realX = 1 + 10 * (x - 1)
            r, _, _ = im.getpixel((realX, realY))
            r /= 255
            line.append(r)
        res.append(line)
    return res

def draw_square(bits):
    im = Image.new('RGB', (len(bits), len(bits[0])))
    for y, line in enumerate(bits):
        for x, b in enumerate(line):
            im.putpixel((x, y), (b * 255, b * 255, b * 255))
    return im

def lines_as_numbers(bits):
    res = []
    for line in bits:
        here = 0
        for b in line:
            here = 2 * here + b
        res.append(here)
    return res

def transpose(bits):
    res = []
    for i in range(len(bits)):
        here = []
        for line in bits:
            here.append(line.pop(0))
        res.append(here)
    return res

if __name__ == '__main__':
    bits53 = get_53x53_bits()
    bits55 = get_55x55_bits()

    with open('53.txt', 'w') as f:
        f.write('\n'.join(map(lambda l: ''.join(map(str, l)), bits53)))
    with open('55.txt', 'w') as f:
        f.write('\n'.join(map(lambda l: ''.join(map(str, l)), bits55)))

    draw_square(bits53).save('53.png')
    draw_square(bits55).save('55.png')

    print 'numbers in 53:'
    print 'rows, big-endian:', lines_as_numbers(bits53)
    print 'rows, little-endian:', lines_as_numbers(map(reverse, bits53))
    bits53t = transpose(bits53)
    print 'cols, big-endian:', lines_as_numbers(bits53t)
    print 'cols, little-endian:', lines_as_numbers(map(reverse, bits53t))
    print ''
    print 'numbers in 55:'
    print 'rows, big-endian:', lines_as_numbers(bits55)
    print 'rows, little-endian:', lines_as_numbers(map(reverse, bits55))
    bits55t = transpose(bits55)
    print 'cols, big-endian:', lines_as_numbers(bits55t)
    print 'cols, little-endian:', lines_as_numbers(map(reverse, bits55t))
