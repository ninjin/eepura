#!/usr/bin/env python

'''
Parse and interact with tokenised/sentence split text by offsets.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-04-09
'''

from string import whitespace

### Constants
WHITESPACE_CHARS = set(whitespace)
###


class Token(object):
    def __init__(self, text, start, end):
        self.text = text
        self.start = start
        self.end = end

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '<Token: text:"{}", start:{}, end:{}>'.format(self.text,
                self.start, self.end)


class Sentence(object):
    def __init__(self, tokens):
        self.tokens = tokens

    def token_by_offset(self, offset):
        # TODO: Inefficient, O(n)
        for tok in self.tokens:
            if tok.start <= offset < tok.end:
                return tok


class Document(object):
    def __init__(self, sentences):
        self.sentences = sentences

    def sentence_by_offset(self, offset):
        # TODO: Inefficient, O(n)
        for sent in self.sentences:
            if sent.tokens[0].start <= offset < sent.tokens[-1].end:
                return sent


def parse_txt_and_tok(txt_data, tok_lines):
    # Read and align the tokens to the text
    sentences = []
    txt_data_i = 0
    for tok_line in tok_lines:
        tok_txts = tok_line.split(' ')
        tok_txts.reverse()

        tokens = []
        while tok_txts:
            tok_txt = tok_txts.pop()
            tok_txt_start = None
            tok_txt_i = 0
            while tok_txt_i < len(tok_txt):
                tok_char = tok_txt[tok_txt_i]
                txt_data_char = txt_data[txt_data_i]

                if tok_char == txt_data_char:
                    if tok_txt_start is None:
                        tok_txt_start = txt_data_i
                    txt_data_i += 1
                    tok_txt_i += 1
                elif (tok_txt_start is None
                        and txt_data_char in WHITESPACE_CHARS):
                    # We allow whitespace mismatches
                    txt_data_i += 1
                else:
                    # TODO: Can be more informative
                    assert 'alignment failure'
            tokens.append(Token(tok_txt, tok_txt_start, txt_data_i))
        sentences.append(Sentence(tokens))
    assert not txt_data[txt_data_i:].strip(), 'not all txt data was aligned'
    return Document(sentences)

if __name__ == '__main__':
    from argparse import ArgumentParser, FileType
    from random import choice, randint
    from sys import argv

    argparser = ArgumentParser('Some simple unittests')
    argparser.add_argument('txt_file', type=FileType('r'))
    argparser.add_argument('tok_file', type=FileType('r'))

    argp = argparser.parse_args(argv[1:])

    txt_data = argp.txt_file.read()
    tok_lines = (l.rstrip('\n') for l in argp.tok_file)

    doc = parse_txt_and_tok(txt_data, tok_lines)

    # Print sentences and tokens
    print 'Document with sentences and tokens:'
    for sent in doc.sentences:
        print ' | '.join(unicode(tok.text) for tok in sent.tokens)
    print

    # Try accessing the sentence by index
    s_i = randint(0, len(doc.sentences) - 1)
    print 'Sentence accessed by index ({}):'.format(s_i)
    rand_s = doc.sentences[s_i]
    print ' | '.join(unicode(tok.text) for tok in rand_s.tokens)
    print

    # Try accessing a token by index
    r_i = randint(0, len(rand_s.tokens) - 1)
    print 'Random token accessed by index ({})'.format(r_i)
    rand_t = rand_s.tokens[r_i]
    print rand_t

    # Finally, try accessing the same random sentence and tokens using offsets
    offset = choice((rand_t.start, rand_t.end - 1, ))
    assert rand_s == doc.sentence_by_offset(offset) == rand_s
    assert rand_t == rand_s.token_by_offset(offset) == rand_t
