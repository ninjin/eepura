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

`nesp` files were converted into stand-off for visualisation and to fit into
the framework using the `nesptost.py` script:

    #!/bin/sh
    for f in `find res/ann -name '*.nesp' | sed -e 's|\.nesp$||g'`
    do
        src/nesptost.py ${f}.{nesp,txt,a1} -t 1000 -e 1000 \
            `if [ -f ${f}.a2 ]; then echo "-a ${f}.a2"; fi;` \
            > ${f}.nesp.st
    done
