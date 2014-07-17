#!/usr/bin/python

import glob
import os
import sys
import math

from PIL import Image

EXTS = 'jpg', 'jpeg', 'JPG', 'JPEG', 'gif', 'GIF', 'png', 'PNG'

def avhash(im):
    if not isinstance(im, Image.Image):
        im = Image.open(im)

    im = im.resize((64, 64), Image.ANTIALIAS).convert('RGB')
    r, g, b = im.split()

    ret = []
    for ir in xrange(4):
        for ig in xrange(4):
            for ib in xrange(4):
                cnt = 0
                for pr, pg, pb in zip(r.getdata(), g.getdata(), b.getdata()):
                    minr, maxr = ir * 64, ir * 64 + 63
                    ming, maxg = ig * 64, ig * 64 + 63
                    minb, maxb = ib * 64, ib * 64 + 63
                    if pr <= maxr and pr >= minr and pg <= maxg and pg >= ming and pb <= maxb and pb >= minb:
                        cnt += 1
                ret.append(cnt)
    return ret

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
        h = avhash(im)

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
            print "%f\t%s" % (ham, f)
