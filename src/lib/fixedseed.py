#!/usr/bin/env python

'''
Perform operations with a fixed seed for a block, then restore the state of
the PRNG. All using the with syntax.

    with FixedSeed(4711):
        ...

Has this already been done? It is quite handy for experiments since it makes
sure that you don't forget to restore the state.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2011-08-24
'''

from random import getstate, seed, setstate

class FixedSeed(object):
    def __init__(self, seed):
        self.seed = seed
        self.state = None

    def __enter__(self):
        self.state = getstate()
        seed(self.seed)
        return self
    
    def __exit__(self, type, value, traceback):
        setstate(self.state)

# Minor test code
if __name__ == '__main__':
    from random import random

    with FixedSeed(4711):
        a = [random() for _ in xrange(17)]
    after_a = random()

    with FixedSeed(4711):
        b = [random() for _ in xrange(17)]
    after_b = random()

    assert a == b
    # Should fail in most cases
    assert after_a != after_b
