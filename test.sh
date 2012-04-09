#!/bin/bash

# Simple suite of tests for development.
#
# Note: This should be turned into a Makefile instead
#
# Author:   Pontus Stenetorp    <pontus stenetorp>
# Version:  2012-03-19

WRK_DIR=wrk

NEG_TRAIN_FEATS=${WRK_DIR}/neg_train.feats
NEG_DEV_FEATS=${WRK_DIR}/neg_dev.feats
SPEC_TRAIN_FEATS=${WRK_DIR}/spec_train.feats
SPEC_DEV_FEATS=${WRK_DIR}/spec_dev.feats

CAT_ID_TO_CATNAME_PICKLE=${WRK_DIR}/catid_to_catname.pickle
FID_TO_FNAME_PICKLE=${WRK_DIR}/fid_to_fname.pickle

NEG_TRAIN_VECS=${WRK_DIR}/neg_train.vecs
NEG_DEV_VECS=${WRK_DIR}/neg_dev.vecs
SPEC_TRAIN_VECS=${WRK_DIR}/spec_train.vecs
SPEC_DEV_VECS=${WRK_DIR}/spec_dev.vecs

NEG_TRAIN_MODEL=${WRK_DIR}/neg_train.model
SPEC_TRAIN_MODEL=${WRK_DIR}/spec_train.model

NEG_DEV_PREDS=${WRK_DIR}/neg_dev.preds
SPEC_DEV_PREDS=${WRK_DIR}/spec_dev.preds

# Just to be sure during testing
rm -rf ${WRK_DIR}
mkdir ${WRK_DIR}

#TRAIN_BIN='ext/liblinear/train -q'
TRAIN_BIN='src/optimisec.py -j 64'
PRED_BIN='ext/liblinear/predict'
#TRAIN_BIN='src/randclassify.py train'
#PRED_BIN='src/randclassify.py classify'

# Merge all training data
./src/featurise.py ${NEG_TRAIN_FEATS} ${SPEC_TRAIN_FEATS} res/ann/{epi,id,ge}/train/
./src/featurise.py ${NEG_DEV_FEATS} ${SPEC_DEV_FEATS} res/ann/{epi,id,ge}/dev/

sort -n -o ${NEG_TRAIN_FEATS} ${NEG_TRAIN_FEATS}
sort -n -o ${SPEC_TRAIN_FEATS} ${SPEC_TRAIN_FEATS}
sort -n -o ${NEG_DEV_FEATS} ${NEG_DEV_FEATS}
sort -n -o ${SPEC_DEV_FEATS} ${SPEC_DEV_FEATS}

src/vectorise.py ${CAT_ID_TO_CATNAME_PICKLE} ${FID_TO_FNAME_PICKLE} < ${NEG_TRAIN_FEATS} > ${NEG_TRAIN_VECS}
src/vectorise.py ${CAT_ID_TO_CATNAME_PICKLE} ${FID_TO_FNAME_PICKLE} < ${SPEC_TRAIN_FEATS} > ${SPEC_TRAIN_VECS}
src/vectorise.py ${CAT_ID_TO_CATNAME_PICKLE} ${FID_TO_FNAME_PICKLE} < ${NEG_DEV_FEATS} > ${NEG_DEV_VECS}
src/vectorise.py ${CAT_ID_TO_CATNAME_PICKLE} ${FID_TO_FNAME_PICKLE} < ${SPEC_DEV_FEATS} > ${SPEC_DEV_VECS}

# XXX: Should optimise C!
${TRAIN_BIN} ${NEG_TRAIN_VECS} ${NEG_TRAIN_MODEL}
${TRAIN_BIN} ${SPEC_TRAIN_VECS} ${SPEC_TRAIN_MODEL}

# XXX: Can be optimised, remove the factor 3!
results() {
    GOLD=$1
    PREDS=$2
    #echo ${GOLD} ${PREDS}
    TP=`grep $'^2\t2$' <(paste <(cut -f 1 -d ' ' ${GOLD}) ${PREDS}) | wc -l`
    FP=`grep $'^2\t1$' <(paste <(cut -f 1 -d ' ' ${GOLD}) ${PREDS}) | wc -l`
    FN=`grep $'^1\t2$' <(paste <(cut -f 1 -d ' ' ${GOLD}) ${PREDS}) | wc -l`
    P=`echo "scale=3; if(${TP} + ${FP} != 0) { ${TP} / (${TP} + ${FP}) } else { 0 }" | bc`
    R=`echo "scale=3; if(${TP} + ${FN} != 0) { ${TP} / (${TP} + ${FN}) } else { 0 }" | bc`
    F=`echo "scale=3; if(${P} + ${R} != 0) { (2 * ${P} * ${R}) / (${P} + ${R}) } else { 0 }" | bc`
    echo TP=${TP} FP=${FP} FN=${FN} P=${P} R=${R} F=${F}
    #echo ${F}
}

echo 'Negation'
${PRED_BIN} ${NEG_DEV_VECS} ${NEG_TRAIN_MODEL} ${NEG_DEV_PREDS} > /dev/null
results ${NEG_DEV_VECS} ${NEG_DEV_PREDS}
echo 'Speculation'
${PRED_BIN} ${SPEC_DEV_VECS} ${SPEC_TRAIN_MODEL} ${SPEC_DEV_PREDS} > /dev/null
results ${SPEC_DEV_VECS} ${SPEC_DEV_PREDS}
