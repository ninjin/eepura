#!/usr/bin/env python

'''
Enrich BioNLP Shared Task (ST) Event Extraction output with Negation and
Speculation annotations by using a few heuristics exploiting existing
automated hedging annotation systems.

Note: Requires annotations to be in BioNLP ST stand-off format.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-03-23
'''

from argparse import ArgumentParser, FileType
from itertools import chain
from sys import stdin, stdout

from lib.ann import parse_ann
from lib.common import Modifier
from lib.heuristic import nesp_heuristic

### Constants
ARGPARSER = ArgumentParser()#XXX:
ARGPARSER.add_argument('negation_speculation_output', type=FileType('r'))
ARGPARSER.add_argument('event_extraction_output', nargs='?',
        type=FileType('r'), default=stdin)#XXX:
ARGPARSER.add_argument('-o', '--output', type=FileType('w'),
        default=stdout)#XXX:
# TODO: Add flags for choosing heuristics
###

def main(args):
    argp = ARGPARSER.parse_args(args[1:])

    ee_anns = [a for a in parse_ann(l.rstrip('\n')
            for l in argp.event_extraction_output)
            if not isinstance(a, str)]
    nesp_anns = [a for a in parse_ann(l.rstrip('\n')
            for l in argp.negation_speculation_output)]

    next_m_num = max(chain((int(a.id[1:]) for a in ee_anns
            if isinstance(a, Modifier)), (0, ))) + 1

    for mark in nesp_heuristic(ee_anns, nesp_anns,
            root_internal=True):
        argp.output.write(unicode(Modifier('M{}'.format(next_m_num),
            mark.type, mark.target)) + '\n')
        next_m_num += 1

    return 0

if __name__ == '__main__':
    from sys import argv
    exit(main(argv))
