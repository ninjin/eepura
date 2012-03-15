'''
Common classes and functions.

Note: Using only a number as id may not have been a genious move, but we will
    roll with it for this set of scripts

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-03-07
'''


class Textbound(object):
    def __init__(self, _id, _type, start, end, comment):
        self.id = _id
        self.type = _type
        self.start = start
        self.end = end
        self.comment = comment

    def __str__(self):
        return 'T{}\t{} {} {}\t{}'.format(self.id, self.type, self.start,
                self.end, self.comment)


class Event(object):
    def __init__(self, _id, _type, trigger, args):
        self.id = _id
        self.type = _type
        self.trigger = trigger
        self.args = args

    def __str__(self):
        return 'E{}\t{}:{}{}'.format(self.id, self.type, self.trigger,
                (' ' + ' '.join('{}:{}'.format(k, v)
                    for k, v in self.args.iteritems())) if self.args else '')


class Modifier(object):
    def __init__(self, _id, _type, target):
        self.id = _id
        self.type = _type
        self.target = target

    def __str__(self):
        return 'M{}\t{} {}'.format(self.id, self.type, self.target)
