#!/usr/bin/python
# -*- coding: utf-8 -*-
from corpuscula import CorpusDict
from corpuscula.corpus_utils import download_syntagrus, syntagrus


# download syntagrus if it's not done yet
download_syntagrus(overwrite=False)
# create and save cdict
CorpusDict(corpus=syntagrus, backup_to='cdict.pickle', log_file=None)
