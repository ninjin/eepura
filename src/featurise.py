#!/usr/bin/env python

'''
Featurise for negation and speculation classification.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2011-03-07
'''

from argparse import ArgumentParser, FileType
from sys import stderr

from lib.corpora import read_corpora_dir

# TODO: Start very very simple, build up-wards
# TODO: Initially share the same feature set

### Constants
ARGPARSER = ArgumentParser()#XXX:
ARGPARSER.add_argument('negation_features', type=FileType('w'))
ARGPARSER.add_argument('speculation_features', type=FileType('w'))
ARGPARSER.add_argument('corpora_dir', nargs='+')
ARGPARSER.add_argument('-v', '--verbose', action='store_true')
#TODO: Feature set argument
###

# TODO: Embed different feature sets

def _featurise_negated(_id, id_to_ann, doc_base):
    e_ann = id_to_ann[_id]
    trigg_ann = id_to_ann[e_ann.trigger]
    # ^ does not occur in the train and dev sets, so it is relatively safe:
    #    sed -e 's| ||g' -e 's|\(.\)|\1\n|g' \
    #        res/ann/{epi,id,ge}/{train,dev}/*.txt | sed '/^$/d' | sort \
    #        | uniq -c | sort -n -r | grep '\^'
    trigger_text = trigg_ann.comment.replace(' ', '^')

    # Feature: The actual text
    yield 'TRIGGER-TEXT-{}'.format(trigger_text)

    # Feature: Prefixes
    for size in xrange(2, min(8, len(trigger_text) + 1)):
        yield 'TRIGGER-PREFIX-{}-{}'.format(size, trigger_text[:size])

    # XXX: Not efficient! Re-done for every f-ing ann!
    ee_anns = [a for a in id_to_ann.itervalues()]
    nesp_path = doc_base + '.nesp.st'
    from lib.ann import parse_ann
    with open(nesp_path, 'r') as nesp_file:
        # XXX: Remove the ugly hack to protect us from newlines!
        nesp_anns = [a for a in parse_ann(l.rstrip('\n') for l in nesp_file if l.strip())]
    from lib.heuristic import nesp_heuristic
    from collections import defaultdict
    for mark in nesp_heuristic(ee_anns, nesp_anns):
        if mark.target == _id:
            heuristic_base = 'HEURISTIC-{}'.upper().format(mark.type)
            yield heuristic_base
            yield heuristic_base + '-' + mark.cue.comment.replace(' ', '^')
            for span_token in mark.span.comment.split():
                yield heuristic_base + '-' + span_token

    # TODO: Feature, neighbour words

    # Event type, actually boosts us a bit, we'll come back to this later
    #yield 'EVENT-TYPE-{}'.format(e_ann.type)

def _featurise_speculated(*args):
    for e in _featurise_negated(*args):
        yield e

def main(args):
    argp = ARGPARSER.parse_args(args[1:])

    seen_negated = 0
    seen_speculated = 0
    for corpora_dir in argp.corpora_dir:
        for doc_id, doc_base, ann_it in read_corpora_dir(corpora_dir):
            if argp.verbose:
                print >> stderr, 'Reading document id: {}'.format(doc_id)

            # Map between annotations and their ids for easy look-up
            ann_id_to_ann = {}
           
            negated = set()
            speculated = set()
            for ann_i, ann in enumerate(a for a in ann_it
                    if not isinstance(a, str)):
                ann_id_to_ann[ann.id] = ann
                if ann.type == 'Negation':
                    negated.add(ann.target)
                elif ann.type == 'Speculation':
                    speculated.add(ann.target)
        
            # XXX: Old, remove
            '''
            try:
                negated = set(ann_id_to_ann[m.target] for m in negations)
                speculated = set(ann_id_to_ann[m.target] for m in speculations)
            except KeyError, e:
                print >> stderr, ('ERROR: Modifier referred to an event with id '
                        '{} for document id {}, but no such event was found'
                        ).format(e.message, doc_id)
                print >> stderr, ann_id_to_ann
                return -1
            '''
        
            seen_negated += len(negated)
            seen_speculated += len(speculated)

            for e_ann_id in (a for a in ann_id_to_ann if a.startswith('E')):
                argp.negation_features.write('{}\t{}\n'.format(
                    1 if e_ann_id in negated else 0,
                    ' '.join('{}:1'.format(f)
                        for f in _featurise_negated(e_ann_id, ann_id_to_ann,
                            doc_base))
                    ))
                argp.speculation_features.write('{}\t{}\n'.format(
                    1 if e_ann_id in speculated else 0,
                    ' '.join('{}:1'.format(f)
                        for f in _featurise_speculated(e_ann_id, ann_id_to_ann,
                            doc_base))
                    ))

            if argp.verbose:
                print >> stderr, 'Read {} annotations'.format(ann_i)

    if argp.verbose:
        print >> stderr, ('Saw a total of {} negated and {} speculated '
                'annotations').format(seen_negated, seen_speculated)

if __name__ == '__main__':
    from sys import argv
    exit(main(argv))
