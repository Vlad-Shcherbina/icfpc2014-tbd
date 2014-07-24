#!/usr/bin/env python2
try:
    from PIL import Image
except:
    print 'sudo pip2 install pillow'

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
    im = im or Image.open('bkg.png')
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

if __name__ == '__main__':
    with open('53.txt', 'w') as f:
        f.write('\n'.join(map(lambda l: ''.join(map(str, l)), get_53x53_bits())))
    with open('55.txt', 'w') as f:
        f.write('\n'.join(map(lambda l: ''.join(map(str, l)), get_55x55_bits())))
