#!/usr/bin/env python

'''
Functionality for interacting with BioNLP ST corpora structures.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-03-15
'''

from os import walk
from os.path import basename, exists, join as path_join, splitext

from ann import parse_ann

def _id(txt_path):
    return splitext(basename(txt_path))[0]

def _read_files(*fpaths):
    for fpath in fpaths:
        with open(fpath, 'r') as f:
            for l in f:
                yield l

def read_corpora_dir(dir_path):
    # The only assumption we can make is that any annotation must have a .txt
    for root, dnames, fnames in walk(dir_path):
        for txt_path in (path_join(root, f) for f in fnames
                if f.endswith('.txt')):
            doc_id = _id(txt_path)
            doc_base = splitext(txt_path)[0]
            ann_files = [f for f in (path_join(root, doc_id + ext)
                for ext in ('.a1', '.a2', )) if exists(f)]
            if not ann_files:
                # Ignore the .txt since it lacks annotations
                continue
            yield doc_id, doc_base, parse_ann(l.rstrip('\n')
                    for l in _read_files(*ann_files))
