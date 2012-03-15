# Makefile controlling experiments and dependencies
#
# Author:	Pontus Stenetorp	<pontus stenetorp se>
# Version:	2012-03-02

EXT_DIR=ext

LIBLINEAR_DIR=${EXT_DIR}/liblinear
LIBLINEAR_DEPS=${shell find ${LIBLINEAR_DIR}/ -type d}
LIBLINEAR_TRAIN_BIN=${LIBLINEAR_DIR}/train
LIBLINEAR_PREDICT_BIN=${LIBLINEAR_DIR}/predict
LIBLINEAR_BINS=${LIBLINEAR_TRAIN_BIN} ${LIBLINEAR_PREDICT_BIN}

${LIBLINEAR_BINS}: ${LIBLINEAR_DEPS}
	cd ${LIBLINEAR_DIR} && make
	touch ${LIBLINEAR_BINS}

.PHONE: all
.DEFAULT_GOAL=all
all: ${LIBLINEAR_BINS}

.PHONY: clean
clean:
	cd ${LIBLINEAR_DIR} && make clean
