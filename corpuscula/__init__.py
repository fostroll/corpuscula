# -*- coding: utf-8 -*-
# Corpuscula project
#
# Copyright (C) 2019-present by Sergei Ternovykh
# License: BSD, see LICENSE for details
"""
Corpuscula is a part of the RuMor project. It is a toolkit that simplifies
corpus processing. Highlights are:

* full CONLL-U support (includes CONLL-U Plus)
* wrappers for known corpora of Russian language
* parser and wrapper for russian part of Wikipedia
* Corpus Dictionary that can be used for further morphology processing
"""
from .conllu import Conllu
from .corpus_dict import CorpusDict
from .items import Items
