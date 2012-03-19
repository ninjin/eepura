#!/usr/bin/env python

assert False, 'XXX: Needs to be updated'

'''
"Enrich" annotation output with textual annotations converted from
a BioScope-ish format.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-03-07
'''

from argparse import ArgumentParser, FileType
from itertools import chain
from sys import stdout

from lib.nesp import parse_and_align_nesp

### Constants
ARGPARSER = ArgumentParser(description='Convert BioText-ish output into '
        'BioNLP Shared-task stand-off')
ARGPARSER.add_argument('nesp_file', type=FileType('r'), help='BioScope-ish output file')
ARGPARSER.add_argument('txt_file', type=FileType('r'), help='text file')
ARGPARSER.add_argument('a1_file', type=FileType('r'), help='a1 file')
ARGPARSER.add_argument('-a', '--a2-file', type=FileType('r'), help='optional a2 file')
###

def main(args):
    argp = ARGPARSER.parse_args(args[1:])

    # Read all event and textbound ids to find the highest used ids
    next_tb_id = 1
    next_e_id = 1
    for ann_line in chain(argp.a1_file,
            argp.a2_file if argp.a2_file is not None else tuple()):
        if not (ann_line.startswith('T') or ann_line.startswith('E')):
            continue

        curr_id = int(ann_line.split('\t', 1)[0].lstrip('TE'))
        if ann_line.startswith('T'):
            next_tb_id = max(next_tb_id, curr_id)
        else:
            next_e_id = max(next_e_id, curr_id)

    # Generate NESP output
    txt_text = argp.txt_file.read()
    parse = parse_and_align_nesp((l.rstrip('\n') for l in argp.nesp_file),
            txt_text)
    for ann in parse.to_standoff(txt_text, next_tb_id=next_tb_id,
            next_e_id=next_e_id):
        stdout.write(str(ann))
        stdout.write('\n')
    
    return 0

if __name__ == '__main__':
    from sys import argv
    exit(main(argv))
