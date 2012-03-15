#!/usr/bin/env python

# TODO: XXX: Clean up this file a bit

'''
Vectorise featurised data.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-01-13
'''

from argparse import ArgumentParser
from atexit import register as atexit_register
from os.path import isfile
from sys import stdin, stdout

try:
    from cPickle import (HIGHEST_PROTOCOL, dump as pickle_dump,
            load as pickle_load)
except ImportError:
    from pickle import (HIGHEST_PROTOCOL, dump as pickle_dump,
            load as pickle_load)

### Constants
ARGPARSER = ArgumentParser()#XXX:
# TODO: Bad name really, it is fid to fname really
ARGPARSER.add_argument('catid_to_catname_pickle')
ARGPARSER.add_argument('fid_to_fname_pickle')
ARGPARSER.add_argument('-t', '--run-unittests', action='store_true')
# TODO: Don't save option!
###


# TODO: Dictionary class wrapper that detects an update, reset check when being unpickled
# TODO: Disallow assignment using other options than put
class IdMapper(dict):
    # TODO: Fix constructor to conform with dict
    def __init__(self, start_id=1):
        self.next_id = 1

    # Override missing for easy access
    def __missing__(self, entry):
        new_id = self.next_id
        self[entry] = new_id
        self.next_id += 1
        return new_id


def _load_pickle(pickle_path, save=True):
    if isfile(pickle_path):
        with open(pickle_path, 'rb') as pickle_file:
            loaded_pickle = pickle_load(pickle_file)
    else:
        loaded_pickle = IdMapper()

    if save:
        atexit_register(_save_pickle_func(loaded_pickle, pickle_path))

    return loaded_pickle

def _save_pickle_func(pickle, pickle_path):
    def save_pickle():
        with open(pickle_path, 'wb') as pickle_file:
            pickle_dump(pickle, pickle_file, HIGHEST_PROTOCOL)
    return save_pickle

def _tests():
    from tempfile import NamedTemporaryFile
    from os import remove

    tmp_path = None
    try:
        tmp_path = NamedTemporaryFile(delete=False).name
        mapper = IdMapper()
        mapper.put('foo')
        _save_pickle_func(mapper, tmp_path)()
        mapper = _load_pickle(tmp_path, save=False)
        assert mapper['foo'] == 1
        mapper.put('bar')
        assert mapper['bar'] == 2
    finally:
        if tmp_path is not None:
            remove(tmp_path)
    return 0

def main(args):
    argp = ARGPARSER.parse_args(args[1:])

    if argp.run_unittests:
        return _tests()

    catid_to_catname = _load_pickle(argp.catid_to_catname_pickle)
    fid_to_fname = _load_pickle(argp.fid_to_fname_pickle)
    
    for line in (l.rstrip('\n') for l in stdin):
        f_type, f_data = line.split('\t')
        f_type_id = catid_to_catname[f_type]
        f_vec = {}
        #print f_data
        for f_name, f_val in ((n, float(v))
                for n, v in (t.rsplit(':', 1)
                    for t in f_data.split(' '))):
            #print f_name, f_val
            f_vec[fid_to_fname[f_name]] = f_val

        stdout.write('{} {}\n'.format(f_type_id, ' '.join(
            '{}:{}'.format(f_id, f_vec[f_id]) for f_id in sorted(f_vec.keys()))))
        #print f_type_id

if __name__ == '__main__':
    from sys import argv
    exit(main(argv))
