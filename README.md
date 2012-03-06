# eepura, eeプラ or ee+ #

This is just a dummy README for now.

## Deta Pre-processing ##

Negation and speculation annotations were stripped using:

    #!/usr/bin/env bash
    for f in `find res -name '*.a2'`
    do
        grep -v -E $'^M[0-9]+\t(Speculation|Negation) ' $f > ${f}.strp
    done
