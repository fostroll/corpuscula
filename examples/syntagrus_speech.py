#!/usr/bin/python
# -*- coding: utf-8 -*-
# Toxic project: Text Preprocessing pipeline
#
# Copyright (C) 2019-present by Sergei Ternovykh
# License: BSD, see LICENSE for details
"""
Example: Make SynTagRus looks like some speech recognition software output.
"""
from corpuscula.conllu import Conllu
from corpuscula.corpus_utils import download_syntagrus, syntagrus, \
                                    AdjustedForSpeech

download_syntagrus(overwrite=False)
Conllu.save(syntagrus.train(), 'syntagrus_train_speech.conllu', fix=True,
            adjust_for_speech=True, log_file=None)
Conllu.save(syntagrus.dev(), 'syntagrus_dev_speech.conllu', fix=True,
            adjust_for_speech=True, log_file=None)
Conllu.save(syntagrus.test(), 'syntagrus_test_speech.conllu', fix=True,
            adjust_for_speech=True, log_file=None)

# NB: if you don't need to save the result, consider the on-fly
# AdjustedForSpeech wrapper:
#
# syntagrus_speech = AdjustedForSpeech(syntagrus)
