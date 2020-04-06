#!/usr/bin/python
# -*- coding: utf-8 -*-

from math import isclose
import filecmp
import os

###
import sys
sys.path.append('../')
###

from tests._test_support import WORK_DIR, WORK_FNAME, \
                                bprint, eprint, safe_run, check_res
import corpuscula
import corpuscula.corpus_utils
import corpuscula.utils

TEST_DNAME = '_test'
TEST_FNAME = 'test.bz2'
TEST_DICT_FNAME = 'test_dict.bz2'
TEST_DPATH = os.path.join(corpuscula.corpus_utils.get_root_dir(),
                          corpuscula.corpus_utils.CORPUS_DNAME, TEST_DNAME)

TEST_FPATH = None
TEST_DICT_FPATH = None
def f ():
    global TEST_FPATH, TEST_DICT_FPATH
    TEST_DICT_FPATH = corpuscula.corpus_utils.get_corpus_fpath(
        dname=TEST_DNAME, fname=TEST_DICT_FNAME
    )
    TEST_FPATH = corpuscula.corpus_utils.get_corpus_fpath(
        dname=TEST_DNAME, fname=TEST_FNAME
    )
    if TEST_DPATH and not os.path.exists(TEST_DPATH):
        os.makedirs(TEST_DPATH, corpuscula.utils.DIR_ACCESS_RIGHTS)
    corpuscula.utils.copy_file(TEST_DICT_FNAME, TEST_DICT_FPATH)
    corpuscula.utils.copy_file(TEST_FNAME, TEST_FPATH)
    return os.path.isfile(TEST_FPATH) and os.path.isfile(TEST_DICT_FPATH)
check_res(safe_run(f, 'Create test corpus'))

corpuscula.corpus_utils.OPENCORPORA_DNAME    = TEST_DNAME
corpuscula.corpus_utils.OPENCORPORA_URL      = TEST_FNAME
corpuscula.corpus_utils.OPENCORPORA_DICT_URL = TEST_DICT_FNAME
def f ():
    global test_corpus, test_corpus_list
    test_corpus = corpuscula.corpus_utils.opencorpora
    #test_corpus_list = list(test_corpus.train())
    return True#len(test_corpus_list) == 12190
check_res(safe_run(f, 'Read test corpus'), err_msg='Wrong corpus length')

def f ():
    res = True
    gold = iter([(2, .3, 0.375), (3, .2, 0.25), (1, .2, 0.25), (4, .1, 0.125)])
    for x in corpuscula.utils.vote([1, 2, 3, 4, 3, 2, 1, 2],
                                   [.1, .1, .1, .1, .1, .1, .1, .1]):
       y = next(gold)
       if x[0] != y[0] or not isclose(x[1], y[1]) or not isclose(x[2], y[2]):
           res = False
           break
    return res
check_res(safe_run(f, 'Testing corpuscula.utils.vote'))

bprint('Testing corpuscula.utils.find_affixes')
check_res(corpuscula.utils.find_affixes('агитпроп', 'Прокофьев'),
          ('агит', 'про', 'п', '', 'Про', 'кофьев'))

bprint('Testing corpuscula.find_file')
check_res(corpuscula.utils.find_file('test_', dname=TEST_DPATH),
          TEST_DICT_FPATH)

bprint('Testing corpuscula.Conllu load/save')
corpuscula.Conllu.save(test_corpus.train(), WORK_FNAME)
res = filecmp.cmp(os.path.join(WORK_DIR, 'test.conllu'), WORK_FNAME)
test = list(corpuscula.Conllu.load(WORK_FNAME))
corpuscula.Conllu.save(test, WORK_FNAME)
check_res(res and filecmp.cmp(os.path.join(WORK_DIR, 'test.conllu'),
                              WORK_FNAME))

def f ():
    sent = ['Съешь', 'же', 'ещё', 'этих', 'мягких',
            'французских булок', ',', 'да', 'выпей', 'чаю', '.']
    test = corpuscula.Conllu.from_sentence(sent)
    test = corpuscula.Conllu.fix([test])
    corpuscula.Conllu.save(test, WORK_FNAME)
    res = filecmp.cmp(os.path.join(WORK_DIR, 'test2.conllu'), WORK_FNAME)
    test = corpuscula.Conllu.from_sentences([sent])
    corpuscula.Conllu.save(test, WORK_FNAME)
    res = filecmp.cmp(os.path.join(WORK_DIR, 'test2.conllu'), WORK_FNAME)
    test = corpuscula.Conllu.from_sentences([sent], split_multi=True)
    corpuscula.Conllu.save(test, WORK_FNAME)
    res = res and filecmp.cmp(os.path.join(WORK_DIR, 'test2_multi.conllu'),
                              WORK_FNAME)
    test = corpuscula.Conllu.from_sentences([sent], split_multi=True,
                                            adjust_for_speech=True)
    corpuscula.Conllu.save(test, WORK_FNAME)
    return res and filecmp.cmp(os.path.join(WORK_DIR, 'test2_speech.conllu'),
                               WORK_FNAME)
check_res(safe_run(f, 'Testing corpuscula.Conllu: '
                      'from_sentence/from_sentences/fix'))

WORK_FNAME = 'test$'
def f ():
    cdict = corpuscula.CorpusDict()
    cdict.backup_to(WORK_FNAME)
    cdict.restore_from(WORK_FNAME)
    cdict = corpuscula.CorpusDict(corpus=test_corpus, format='conllu_parsed',
                                  backup_to=WORK_FNAME)
    cdict = corpuscula.CorpusDict(restore_from=WORK_FNAME)
    def g ():
        return len(cdict._wforms   ) == 20507 \
           and len(cdict._lemmata  ) == 12913 \
           and len(cdict._tags     ) == len(cdict.get_tags()) == 22 \
           and len(cdict._feats    ) == len(cdict.get_feats()) == 53 \
           and len(cdict._feat_vals) == 53 \
           and cdict.predict_tag('искусства') == ('NOUN', 0.75) \
           and cdict.predict_lemma('искусства', 'NOUN') == \
               ('искусство', 0.75) \
           and cdict.predict_feat('CAse', 'искусства',
                                  'искусство', 'NOUN') == ('gent', 0.75)
    res = g()
    cdict = corpuscula.CorpusDict(corpus=os.path.join(WORK_DIR,
                                                      'test.conllu'))
    return res and g()
check_res(safe_run(f, 'Testing corpuscula.CorpusDict'))

os.remove(WORK_FNAME)

safe_run(lambda: corpuscula.corpus_utils.remove_corpus(TEST_DNAME),
         'Remove test corpus')
check_res(os.path.isdir(TEST_DPATH), False)
