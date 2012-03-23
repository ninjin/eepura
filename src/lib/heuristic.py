'''
Heuristic for enriching Event Extraction annotation using existing NESP
annotations.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-03-23
'''

from itertools import chain

from lib.common import Event, Textbound


class Span(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __contains__(self, index):
        return self.start <= index < self.end


def _get_neg_and_spec_spans(nesp_anns):
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
        span = Span(span_ann.start, span_ann.end)
        if span_ann.id in negated_ids:
            neg_spans.append(span)
        if span_ann.id in speculated_ids:
            spec_spans.append(span)

    return neg_spans, spec_spans

def nesp_heuristic(ee_anns, nesp_anns, root_internal=True):
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

            if root_internal:
                any_arg = True #XXX: Determine the optimal here
                # Prune all events that are arguments of other events
                # TODO: Chop this up
                to_prune = set(chain(*[[v for k, v in a.args.iteritems()
                        if any_arg or k in set(('Theme', ))]
                    for a in events_in_span]))
                events_in_span = [a for a in events_in_span
                        if a.id not in to_prune]
                
            for e_ann in events_in_span:
                if e_ann.id not in marked_events:
                    yield (span_type, e_ann.id)
                    marked_events.add(e_ann.id)
