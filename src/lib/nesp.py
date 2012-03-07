#!/usr/bin/env python

'''
Parsing logic for BiographTA NeSp Scope Labeler output format (it should be in
BioScope format, but I don't dare to call the output from this thing official
BioScope since the output is FUBAR when it comes to its' XML-ishness).

BiographTA NeSp Scope Labeler:

    http://www.clips.ua.ac.be/BiographTA/software.html

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2011-10-19
'''

# TODO: Fix character width

from collections import defaultdict
from re import compile as re_compile
from string import whitespace

from common import Event, Textbound

### Constants
WHITESPACE_CHARS = set(whitespace)

SENTENCE_REGEX = re_compile(
        r'<sentence id="(?P<id>[0-9]+)">(?P<content>.*?)</sentence>$')
# Note: We assume that the order is type, then id for the attributes. We have
#   an assert to catch if this fails.
SCOPE_REGEX = re_compile(
        r'(?P<s_tag><scope type="(?P<type>[^"]+)" '
        r'id="(?P<id>[0-9]+)">)(?P<content>.*?)(?P<e_tag></scope>)')
CUE_REGEX = re_compile(
        r'(?P<s_tag><cue type="(?P<type>[^"]+)" '
        r'id="(?P<id>[0-9]+)">)(?P<content>.*?)(?P<e_tag></cue>)')
# Ultra liberal, but should suit our purpose
XML_TAG_REGEX = re_compile(r'<(?:/)?[a-zA-Z]+[^ ]*(?: [^>]*)?(?:/)?>')
###


# Keey track of a collection of spans as their text is manipulated
class NESPSpans(object):
    def __init__(self):
        self.data = defaultdict(dict)

    def insert(self, span, elem, _type, id):
        assert id not in self.data[elem]
        self.data[elem][id] = (span, _type)

    def deletion(self, del_span, text):
        # Move all spans so that they are in sync
        for elem in self.data:
            for _id in self.data[elem]:
                span, _type = self.data[elem][_id]
                diff = del_span[1] - del_span[0]
                new_span = span
                # Have we been shifted? If so, move us back accordingly.
                if del_span[0] < span[0] and del_span[1] <= span[0]:
                    # Deletion prior to this span, move both start and end
                    new_span = [span[0] - diff, span[1] - diff]
                elif del_span[0] >= span[0] and del_span[1] <= span[1]:
                    # Deletion inside this span
                    new_span = [span[0], span[1] - diff]
                elif del_span[0] >= span[1] and del_span[1] > span[1]:
                    # Deletion after this span, do nothing
                    pass
                else:
                    assert False, 'deletion across span boundary'

                # Potentially update the data
                self.data[elem][_id] = (new_span, _type)

    def translate(self, trans):
        for elem in self.data:
            for _id in self.data[elem]:
                span, _type = self.data[elem][_id]
                self.data[elem][_id] = ([trans[span[0]], trans[span[1]]], _type)

    def to_standoff(self, text):
        next_e_id = 1
        next_tb_id = 1
        # Note: We are assuming sanity all the way here
        for cue_id, cue_data in self.data['cue'].iteritems():
            cue_offsets, cue_type = cue_data
            cue_start, cue_end = cue_offsets
            
            scope_offsets, _ = self.data['scope'][cue_id]
            scope_start, scope_end = scope_offsets

            event_type = {
                    'neg': 'Negation',
                    'spec': 'Speculation',
                    }[cue_type]

            # Trigger annotation
            cue_id = 'T{}'.format(next_tb_id)
            yield Textbound(next_tb_id, event_type, cue_start, cue_end,
                    text[cue_start:cue_end])
            next_tb_id += 1
            scope_id = 'T{}'.format(next_tb_id)

            args = {
                    'Scope': scope_id,
                    }

            # Event annotation
            yield Event(next_e_id, event_type, cue_id, args)
            next_e_id += 1

            yield Textbound(next_tb_id, 'Span', scope_start, scope_end,
                    text[scope_start:scope_end])
            next_tb_id += 1


def _contains_xml_tag(s):
    return XML_TAG_REGEX.search(s) is not None

def parse_and_align_nesp(nesp_lines, txt_text):
    # Rant: What ever the fuck this nesp thing is, it isn't XML in any
    #   meaning of the god damn word, it doesn't have proper character escapes
    #   etc. so it is easier to parse it using god damn regular expressions
    #   than treating it as XML. In many ways I hate XML with a passion, but
    #   what I hate even more than XML is retarded formats posing as XML.

    # Some trickery is necessary to make this work, we first need a mapping
    # between the offsets for the stand-off and the BioScope "XML"

    nesp_line_strs = []
    for nesp_line in nesp_lines:
        s_match = SENTENCE_REGEX.match(nesp_line)
        assert s_match is not None
        nesp_line_strs.append(s_match.groupdict()['content'])
    # We now have some text but it most likely still contains XML
    nesp_text = '\n'.join(nesp_line_strs)

    # Mine the marked XML-ish spans and extract the actual text
    spans = NESPSpans()
    for r_type, regex in (('scope', SCOPE_REGEX), ('cue', CUE_REGEX), ):
        # Remove the spans
        while True:
            m = regex.search(nesp_text)
            if m is None:
                # Done with this tag
                break

            # Remove the tags from the tex
            gdic = m.groupdict()
            spans.insert(m.span(4), r_type, gdic['type'], gdic['id'])
            s_tag_span = m.span(1)
            spans.deletion(s_tag_span, nesp_text)
            nesp_text = nesp_text[:s_tag_span[0]] + nesp_text[s_tag_span[1]:]
            # Compensating for the removal of the start tag
            e_tag_span = [e - (s_tag_span[1] - s_tag_span[0]) for e in m.span(5)]
            spans.deletion(e_tag_span, nesp_text)
            nesp_text = nesp_text[:e_tag_span[0]] + nesp_text[e_tag_span[1]:]

    assert not _contains_xml_tag(nesp_text), 'xml remains after clean-up: ' + nesp_text

    nesp_to_txt_index_map = {}
    txt_i = 0
    nesp_i = 0
    while True:
        if txt_i >= len(txt_text) or nesp_i >= len(nesp_text):
            break
        txt_c = txt_text[txt_i]
        nesp_c = nesp_text[nesp_i]
        if txt_c == nesp_c:
            nesp_to_txt_index_map[nesp_i] = txt_i
            txt_i += 1
            nesp_i += 1
        elif txt_c in WHITESPACE_CHARS:
            txt_i += 1
        # nesp has some really fucked up escapes(?) using inserted = signs
        #   we allow to ignore equal marks and hope for the best:
        #
        #   Example: "PKD1/3-/-:" => "PKD1/3==-==/==- = = :"
        #
        #   My best guess is that they have escaped hyphens and then ran a
        #   tokeniser over it, nice, that is easily reversible (not).
        elif nesp_c in WHITESPACE_CHARS or nesp_c == '=':
            nesp_to_txt_index_map[nesp_i] = None
            nesp_i += 1
        else:
            #print txt_c, nesp_c
            assert False
    # Iterate backwards and fill in the indices for erased chars as the
    #   next character in the text file
    ids = sorted(e for e in nesp_to_txt_index_map)
    for i in ids[::-1]:
        if nesp_to_txt_index_map[i] is None:
            nesp_to_txt_index_map[i] = last_val
        else:
            last_val = nesp_to_txt_index_map[i]
    # For anything beyond the final index we give the max
    d = defaultdict(lambda : ids[-1])
    for k, v in nesp_to_txt_index_map.iteritems():
        d[k] = v
    nesp_to_txt_index_map = d
    spans.translate(nesp_to_txt_index_map)

    return spans

if __name__ == '__main__':
    # From: PMID-10794570 and PMID-18326024
    test_txt_str = (
            'It was also shown that the ability to label chromosomes could '
            'vary drastically with different fixation procedures, adding '
            'further complications to interpretation of the potentially '
            'complex role of phosphorylated histone H1 in chromatin '
            'condensation or decondensation.'

            'The level or distribution of acetylated alpha-tubulin was not '
            'altered in HDAC3-deficient cells.'
            )
    test_nesp_str = (
            '<sentence id="5">It was also shown that the ability to label '
            'chromosomes <scope type="spec" id="0"> <cue type="spec" id="0">'
            'could</cue> vary drastically with different fixation procedures'
            '</scope> , adding further complications to interpretation of '
            'the <scope type="spec" id="1"> <cue type="spec" id="1">'
            'potentially</cue> complex</scope> role of phosphorylated '
            'histone H1 in chromatin condensation or decondensation .'
            '</sentence>',

            '<sentence id="11"><scope type="neg" id="5">The level or '
            'distribution of acetylated alpha-tubulin was <cue type="neg" '
            'id="5">not</cue> altered in HDAC3-deficient cells</scope> .'
            '</sentence>',
            )
    spans = parse_and_align_nesp(test_nesp_str, test_txt_str)
    for ann in spans.to_standoff(test_txt_str):
        print ann
