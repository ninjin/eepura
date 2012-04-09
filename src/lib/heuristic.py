'''
Heuristic for enriching Event Extraction annotation using existing NESP
annotations.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-03-23
'''

from collections import namedtuple
from itertools import chain

from lib.common import Event, Textbound

Marked = namedtuple('Marked', ('target', 'type', 'cue', 'span', 'root', ))

def _get_neg_and_spec_spans(nesp_anns):
    id_to_ann = {}
    for ann in nesp_anns:
        id_to_ann[ann.id] = ann

    negated_ids = set()
    speculated_ids = set()
    for e_ann in (a for a in nesp_anns if isinstance(a, Event)):
        if e_ann.type == 'Negation':
            negated_ids.add(e_ann.args['Scope'])
        elif e_ann.type == 'Speculation':
            speculated_ids.add(e_ann.args['Scope'])

    neg_spans = []
    spec_spans = []
    for span_ann in (a for a in nesp_anns
            if isinstance(a, Textbound) and a.type == 'Span'):
        #XXX: HORRIBLE HACK!
        for cue_ann in (a for a in nesp_anns
                if isinstance(a, Event)):
            if cue_ann.args['Scope'] == span_ann.id:
                break
        else:
            assert False
        span_ann.cue = id_to_ann[cue_ann.trigger]
        if span_ann.id in negated_ids:
            neg_spans.append(span_ann)
        if span_ann.id in speculated_ids:
            spec_spans.append(span_ann)

    return neg_spans, spec_spans

def nesp_heuristic(ee_anns, nesp_anns):
    neg_spans, spec_spans = _get_neg_and_spec_spans(nesp_anns)

    id_to_ann = {}
    for ann in ee_anns:
        id_to_ann[ann.id] = ann

    # This portion is not optimal, but will do for now
    for span_type, spans in (('Negation', neg_spans),
            ('Speculation', spec_spans), ):
        # Only report each event as negated or speculated once
        marked_events = set()
        for span in spans:
            events_in_span = [a for a in ee_anns
                    if isinstance(a, Event)
                    and id_to_ann[a.trigger].start in span
                    and id_to_ann[a.trigger].end <= span.end]

            any_arg = True #XXX: Determine the optimal here
            # Prune all events that are arguments of other events
            # TODO: Chop this up
            non_root_marked_events = set(chain(*[[v for k, v in a.args.iteritems()
                    if any_arg or k in set(('Theme', ))]
                for a in events_in_span]))
                
            for e_ann in events_in_span:
                if e_ann.id not in marked_events:
                    # TODO: XXX: This is a hack, fix it later!
                    #print span
                    yield Marked(target=e_ann.id, type=span_type,
                            #XXX: CUE!
                            cue=span.cue, span=span,
                            root=e_ann.id not in non_root_marked_events)
                    marked_events.add(e_ann.id)
