#!/usr/bin/python

import glob
import os
import sys
import math

from PIL import Image

EXTS = 'jpg', 'jpeg', 'JPG', 'JPEG', 'gif', 'GIF', 'png', 'PNG'

def dhash(im, hash_size = 8):
    if not isinstance(im, Image.Image):
        im = Image.open(im)

    im = im.convert('L').resize(
        (hash_size + 1, hash_size),
        Image.ANTIALIAS,
    )
 
    pixels = list(im.getdata())
 
    difference = []
    for row in xrange(hash_size):
        for col in xrange(hash_size):
            pixel_left = im.getpixel((col, row))
            pixel_right = im.getpixel((col + 1, row))
            difference.append(pixel_left > pixel_right)
 
    decimal_value = 0
    hex_string = []
    for index, value in enumerate(difference):
        if value:
            decimal_value += 2**(index % 8)
        if (index % 8) == 7:
            hex_string.append(decimal_value)
            decimal_value = 0

    return hex_string

def hamming(h1, h2):
    # Cosine similarity
    son = reduce(lambda x, (y, z): x + y * z, zip(h1, h2), 0)
    mom1 = math.sqrt(reduce(lambda x, y: x + y * y, h1, 0))
    mom2 = math.sqrt(reduce(lambda x, y: x + y * y, h2, 0))
    return son / (mom1 * mom2)

if __name__ == '__main__':
    if len(sys.argv) <= 1 or len(sys.argv) > 3:
        print "Usage: %s image.jpg [dir]" % sys.argv[0]
    else:
        im, wd = sys.argv[1], '.' if len(sys.argv) < 3 else sys.argv[2]
        h = dhash(im)

        os.chdir(wd)
        images = []
        for ext in EXTS:
            images.extend(glob.glob('*.%s' % ext))

        seq = []
        prog = int(len(images) > 50 and sys.stdout.isatty())
        for f in images:
            seq.append((f, hamming(dhash(f), h)))
            if prog:
                perc = 100. * prog / len(images)
                x = int(2 * perc / 5)
                print '\rCalculating... [' + '#' * x + ' ' * (40 - x) + ']',
                print '%.2f%%' % perc, '(%d/%d)' % (prog, len(images)),
                sys.stdout.flush()
                prog += 1

        if prog: print
        for f, ham in sorted(seq, key=lambda i: i[1]):
            print "%f\t%s" % (ham, f)
