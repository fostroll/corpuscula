# -*- coding: utf-8 -*-
# Corpuscula project
#
# Copyright (C) 2019-present by Sergei Ternovykh
# License: BSD, see LICENSE for details
"""
Corpuscula is a part of the RuMor project. It is a toolkit that simplifies
corpus processing. Highlights are:

* full CoNLL-U support (includes CoNLL-U Plus)
* wrappers for known corpora of Russian language
* parser and wrapper for russian part of Wikipedia
* Corpus Dictionary that can be used for further morphology processing
"""
from corpuscula._version import __version__
from corpuscula.conllu import Conllu
from corpuscula.corpus_dict import CorpusDict
from corpuscula.items import Items
