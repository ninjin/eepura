#!/usr/bin/env python

'''
Random classifier, reads liblinear style "training" data to register the
labels and then assign equal probability to all of them.
Intended to be used as a drop-in replacement for liblinear in an evaluation
pipeline.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-03-19
'''

from argparse import ArgumentParser, FileType
from random import choice
from sys import stdout

### Constants
ARGPARSER = ArgumentParser()#XXX:
ARGPARSER.add_argument('action', choices=('train', 'classify', ))
ARGPARSER.add_argument('data_path')
ARGPARSER.add_argument('model_path')
# Note: Ugly hack to use results_path like this, but is similar to liblinear
ARGPARSER.add_argument('results_path', nargs='?', default='/dev/stdout')
###

def _train(argp):
    lbls = set()
    with open(argp.data_path, 'r') as data:
        for lbl in (l.split(' ', 1)[0] for l in data):
            lbls.add(lbl)

    with open(argp.model_path, 'w') as model:
        for lbl in sorted([l for l in lbls], key=int):
            model.write('{}\n'.format(lbl))

def _classify(argp):
    # Read the "model"
    lbls = set()
    with open(argp.model_path, 'r') as model:
        for lbl in (int(l.rstrip('\n')) for l in model):
            lbls.add(lbl)
    lbls = [lbl for lbl in lbls]
    lbls.sort()

    with open(argp.data_path, 'r') as data:
        with open(argp.results_path, 'w') as results:
            for _ in data:
                results.write('{}\n'.format(choice(lbls)))
    return 0

def main(args):
    argp = ARGPARSER.parse_args(args[1:])
    if argp.action == 'train':
        return _train(argp)
    elif argp.action == 'classify':
        return _classify(argp)
    else:
        assert False, 'unknown action'

if __name__ == '__main__':
    from sys import argv
    exit(main(argv))
