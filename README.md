# eepura, eeプラ or ee+ #

This is just a dummy README for now.

## Data Pre-processing ##

This section is probably not interesting to anyone but left in for personal
reference and for those that really want to replicate each conversion step up
until the experimental scripts take over.

Negation and speculation annotations were stripped using:

    #!/usr/bin/env bash
    for f in `find res -name '*.a2'`
    do
        grep -v -E $'^M[0-9]+\t(Speculation|Negation) ' $f > ${f}.strp
    done

Filenames were corrected for the `nesp` files since for some reason they
violated the original BioNLP ST naming conventions by containing spaces:

    #!/bin/sh
    find res -name '* *.nesp' | while read f
    do
        mv "$f" `echo $f | sed -e 's| |_|g'`
    done
