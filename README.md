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

## Frequently Asked Questions (FAQ) ##

* Q: Why the name `eepura`?
* A: `eepura` was developed at the University of Tokyo and draws some
    inspiration from Japanese. In Japanese C++ can be written shiipurasupurasu
    (シープラスプラス) and due to the wonderful nature of the Japanese
    language purasu (プラス) naturally becomes pura (プラ) for short, then due
    to yet another wonderful aspect of Japanese it is not uncommon to drop
    repeated patterns in expressions (happens with Japanese onomatopoeitic
    expressions quite frequently, but that is a completely different story)
    so informally C++ is shiipura (シープラ). Stroustrup intended the C++ name
    to signify the extension of the C language, thus building a system that
    enhances the output of existing event extraction systems would be...

* Q: Is this really a FAQ?
* A: Not really, no, mostly it is just a bunch of questions that might be
    raised written while waiting for the model to be trained during
    experiments
