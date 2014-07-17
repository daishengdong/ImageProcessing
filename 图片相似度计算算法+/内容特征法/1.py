#!/usr/bin/python

import glob
import os
import sys

from PIL import Image

EXTS = 'jpg', 'jpeg', 'JPG', 'JPEG', 'gif', 'GIF', 'png', 'PNG'

# Otsu's method
def OtsuThresholding(im):
    histData = [0 for i in xrange(64 * 64)]
    for pixel in im.getdata():
       histData[0xFF & pixel] += 1

    total = len(im.getdata())
    sum_ = reduce(lambda x, (i, y): x + i * y, enumerate(histData), 0)

    sumB, wB, wF, varMax, threshold = 0, 0, 0, 0, 0
    for t in xrange(1 << 8):
        wB += histData[t]
        if wB == 0:
            continue

        wF = total - wB
        if wF == 0:
            break

        sumB += t * histData[t]

        mB = sumB / wB
        mF = (sum_ - sumB) / wF

        varBetween = wB * wF * (mB - mF) * (mB - mF)

        if varBetween > varMax:
            varMax = varBetween
            threshold = t

    return threshold

def avhash(im):
    if not isinstance(im, Image.Image):
        im = Image.open(im)
    im = im.resize((8, 8), Image.ANTIALIAS).convert('L')
    threshold = OtsuThresholding(im)
    return reduce(lambda x, (y, z): x | (z << y),
                  enumerate(map(lambda i: 0 if i < threshold else 1, im.getdata())),
                  0)

def hamming(h1, h2):
    h, d = 0, h1 ^ h2
    while d:
        h += 1
        d &= d - 1
    return h

if __name__ == '__main__':
    if len(sys.argv) <= 1 or len(sys.argv) > 3:
        print "Usage: %s image.jpg [dir]" % sys.argv[0]
    else:
        im, wd = sys.argv[1], '.' if len(sys.argv) < 3 else sys.argv[2]
        h = avhash(im)

        print h
        i = raw_input()

        os.chdir(wd)
        images = []
        for ext in EXTS:
            images.extend(glob.glob('*.%s' % ext))

        seq = []
        prog = int(len(images) > 50 and sys.stdout.isatty())
        for f in images:
            seq.append((f, hamming(avhash(f), h)))
            if prog:
                perc = 100. * prog / len(images)
                x = int(2 * perc / 5)
                print '\rCalculating... [' + '#' * x + ' ' * (40 - x) + ']',
                print '%.2f%%' % perc, '(%d/%d)' % (prog, len(images)),
                sys.stdout.flush()
                prog += 1

        if prog: print
        for f, ham in sorted(seq, key=lambda i: i[1]):
            print "%d\t%s" % (ham, f)
