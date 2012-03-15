#!/usr/bin/env python

'''
Parsing and handling BioNLP ST annotation files.

Note: This is a very naive and rudimentary parser that only works well for
    this project, nothing fancy

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-03-07
'''

from common import Textbound, Event, Modifier

### Constants
ID_PREFIXES = set(('T', 'E', 'M'))
###

def parse_ann(ann_lines):
    for ann_line in ann_lines:
        if ann_line[0] in ID_PREFIXES:
            ann_id = int(ann_line.split('\t')[0].lstrip(''.join(ID_PREFIXES)))
            if ann_line.startswith('T'):
                tb_data, tb_comment = ann_line.split('\t')[1:]
                tb_type, tb_start, tb_end = tb_data.split(' ')
                yield Textbound(ann_id, tb_type, int(tb_start), int(tb_end),
                        tb_comment)
            elif ann_line.startswith('E'):
                trigg_data, arg_data = ann_line.split('\t')[1].split(' ', 1)
                trigg_type, trigg_id = trigg_data.split(':')
                args = dict(a.split(':') for a in arg_data.split(' '))
                yield Event(ann_id, trigg_type, trigg_id, args)
            elif ann_line.startswith('M'):
                mod_type, mod_tgt = ann_line.split('\t')[1].split(' ')
                yield Modifier(ann_id, mod_type, mod_tgt)
            else:
                assert False, 'unknown annotation type'
        else:
            # We don't care to parse this, let it pass
            yield ann_line

if __name__ == '__main__':
    # Half made-up, half real
    test_ann_str = (
        '*\tEquiv T9 T10',
        'T1\tPositive_regulation 0 10\tActivation',
        'T2\tGene_expression 197 220\tearly growth response-1',
        'T3\tRegulation 227 232\tEGR-1',
        'T4\tPositive_regulation 273 278\tEGR-1',
        'T5\tReguralation 391 396\tEGR-1',
        'T6\tProtein 430 463\tchloramphenicol acetyltransferase',
        'T7\tProtein 465 468\tCAT',
        'T8\tProtein 505 510\tEGR-1',
        'T9\tProtein 576 581\tEGR-1',
        'T10\tProtein 703 724\tserum response factor',
        'E1\tPositive_regulation:T1 Theme:E2',
        'E2\tGene_expression:T2 Theme:T10',
        'E3\tRegulation:T3 Theme:E4',
        'E4\tPositive_regulation:T4 Theme:T9 Cause:E1', 
        'E5\tRegulation:T5 Theme:E3',
        'M1\tNegation E1',
            )

    for ann in parse_ann(test_ann_str):
        print ann
