# -*- coding: utf-8 -*-
# Corpuscula project: Corpus Dictionary
#
# Copyright (C) 2019-present by Sergei Ternovykh
# License: BSD, see LICENSE for details
"""
A corpus dictionary to use for further morphology processing. It contains
a bunch of useful statictics and the generator of LEMMA by the word FORM and
POS tag.
"""
from operator import itemgetter
import pickle
import sys

from .conllu import Conllu
from .corpus_utils import _AbstractCorpus
from .utils import LOG_FILE, find_affixes, print_progress


class CorpusDict:
    """Arrays of information extracted from labeled corpus(es).
    May be used for a lot of text processing tasks"""

    def __init__(self, restore_from=None, corpus=None, format='conllu',
                 backup_to=None, cnt_thresh=20, ambiguity_thresh=1.,
                 log_file=LOG_FILE):
        """
        :param restore_from: path to backup file to load from
        :type restore_from: str
        :param corpus: path to file in known format or list of already parsed
                       sentences
        :type corpus: str|list(dict())
        :param format: known format: 'conllu'|'conllu_parsed'
        :type format: str
        :param backup_to: path to backup file to save to
        :type backup_to: str
        :param cnt_thresh: param for ``fit()``
        :param ambiguity_thresh: param for ``fit()``
        :param log_file: stream for info messages
        :type file

        NB: If both *restore_from* and *corpus* are not None then information
        extracted from *corpus* will be added to state restored from backup"""
        self._cnt_thresh       = cnt_thresh
        self._ambiguity_thresh = ambiguity_thresh

        self._wforms    = []  # [wform]
        self._lemmata   = []  # [lemma]
        self._tags      = []  # [tag]
        self._feats     = []  # [feat]
        self._feat_vals = []  # [[val]]

        self._wforms_id    = {}  # {wform: id}
        self._lemmata_id   = {}  # {lemma: id}
        self._tags_id      = {}  # {tag: id}
        self._feats_id     = {}  # {feat: id}
        self._feat_vals_id = []  # [{val: id}]

        self._tags_freq = []       # [(tag, cnt, freq)], sorted by freq
        self._feats_freq = {}      # {tag: [(feat, cnt, freq)]}, sorted by freq
        self._feat_vals_freq = {}  # {tag: {feat: [(val, cnt, freq)]}},
                                   # sorted by freq

        self._wform_tag_cnts  = {}  # {wform_id: {tag_id: {lemma_id: cnt}}}
        self._wform_feat_cnts = {}
            # {wform_id: {tag_id: {lemma_id: {feat_id: {val_id: cnt}}}}}
            #                                 '--- may be empty ---'
        self._lemma_tag_cnts  = {}  # {lemma_id: {tag_id: cnt}}
        self._lemma_feat_cnts = {}
            # {lemma_id: {tag_id: {feat_id: {val_id: cnt}}}}
            #                      '--- may be empty ---'

        self._most_probable_tags        = {}    # {wform_id: tag_id}
        self._most_common_tag           = None  # tag
        self._common_endings            = {}
            # {tag_id: {wform_ed: [(lemma_ed, cnt)]})
            # [(lemma_ed, cnt)] sorted by cnt
        self._capitalized_tags          = set() # set(tag_id)
        self._tag_feats                 = []    # [set(feat_id)]
        self._most_probable_wform_feats = {}    # {wform_id: {feat_id: val_id}}
        self._most_probable_lemma_feats = {}    # {lemma_id: {feat_id: val_id}}

        if restore_from:
            self.restore_from(restore_from)
        if corpus:
            self.parse(corpus, format=format, log_file=log_file)
        if backup_to:
            self.backup_to(backup_to)
        if corpus:
            self.fit()

    def backup(self):
        """Get current state"""
        return {'_cnt_thresh'      : self._cnt_thresh      ,
                '_ambiguity_thresh': self._ambiguity_thresh,
                '_wforms_id'       : self._wforms_id       ,
                '_lemmata_id'      : self._lemmata_id      ,
                '_tags_id'         : self._tags_id         ,
                '_feats_id'        : self._feats_id        ,
                '_feat_vals_id'    : self._feat_vals_id    ,
                '_wform_tag_cnts'  : self._wform_tag_cnts  ,
                '_wform_feat_cnts' : self._wform_feat_cnts ,
                '_lemma_tag_cnts'  : self._lemma_tag_cnts  ,
                '_lemma_feat_cnts' : self._lemma_feat_cnts }

    def backup_to(self, file_path):
        """Store current state to file"""
        with open(file_path, 'wb') as f:
            pickle.dump(self.backup(), f, 2)

    def restore(self, o):
        """Restore current state from backup object"""
        (self._cnt_thresh      ,
         self._ambiguity_thresh,
         self._wforms_id       ,
         self._lemmata_id      ,
         self._tags_id         ,
         self._feats_id        ,
         self._feat_vals_id    ,
         self._wform_tag_cnts  ,
         self._wform_feat_cnts ,
         self._lemma_tag_cnts  ,
         self._lemma_feat_cnts ) = [o[x] for x in ['_cnt_thresh'      ,
                                                   '_ambiguity_thresh',
                                                   '_wforms_id'       ,
                                                   '_lemmata_id'      ,
                                                   '_tags_id'         ,
                                                   '_feats_id'        ,
                                                   '_feat_vals_id'    ,
                                                   '_wform_tag_cnts'  ,
                                                   '_wform_feat_cnts' ,
                                                   '_lemma_tag_cnts'  ,
                                                   '_lemma_feat_cnts' ]]
        self._wforms = list(k for k, _ in
            sorted(self._wforms_id.items(), key=itemgetter(1)))
        self._lemmata = list(k for k, _ in
            sorted(self._lemmata_id.items(), key=itemgetter(1)))
        self._tags = list(k for k, _ in
            sorted(self._tags_id.items(), key=itemgetter(1)))
        self._feats = list(k for k, _ in
            sorted(self._feats_id.items(), key=itemgetter(1)))
        self._feat_vals = list(
            [k for k, _ in sorted(vals.items(), key=itemgetter(1))]
                for vals in self._feat_vals_id
        )
        self.fit()

    def restore_from(self, file_path):
        """Restore current state from file"""
        with open(file_path, 'rb') as f:
            self.restore(pickle.load(f))

    def isempty(self):
        """Check if current state is not contain any information"""
        return not self._wforms

    def parse(self, corpus, format='conllu', append=False, log_file=LOG_FILE):
        """Extract useful information from a *corpus* given.

        :param corpus: path to file in known format or list of already parsed
                       sentences
        :type corpus: str|list(dict())
        :param format: known format: 'conllu'|'conllu_parsed'
        :type format: str
        :param append: if False then method will throw exception if current
                       state is not empty
        :type append: bool
        :param log_file: stream for info messages
        :type file
        """
        assert self.isempty() or append, 'Error: Current state is not ' \
            'empty. Use append=True to append next corpus'
        assert format in ['conllu', 'conllu_parsed'], \
            "Error: Invalid format '{}'".format(format)
        if isinstance(corpus, type) and issubclass(corpus,
                                                   _AbstractCorpus):
            corpus = corpus.train()
        elif format == 'conllu':
            corpus = Conllu.load(corpus, log_file=None)
        corpus_len = None if format == 'conllu' else \
                     len(corpus) if isinstance(corpus, list) else \
                     None
        progress_step = max(int(corpus_len / 60), 1000) if corpus_len else 1000
        progress_check_step = min(int(corpus_len / 100), 1000) \
                                  if corpus_len else 100

        if log_file:
            print('Parse corpus', file=log_file)
        ntoken = 0
        nyo = 0
        sent_no = -1
        for sent_no, sentence in enumerate(corpus):
            if log_file and not sent_no % progress_check_step:
                print_progress(sent_no, end_value=corpus_len,
                               step=progress_step, file=log_file)
            if isinstance(sentence, tuple):
                sentence = sentence[0]
            for token in sentence:
                id_, wform, lemma, tag, feats = [
                    token[x] for x in ['ID', 'FORM', 'LEMMA', 'UPOS', 'FEATS']
                ]
                if wform and '-' not in id_ \
               and not any(x.isdecimal() for x in wform) \
               and not any(x.isdecimal() for x in lemma):
                    ntoken += 1
                    # if wform contain Russian "yo" letter, we'll add both two
                    # wforms instead of one: with and without "yo" with the
                    # same lemma and other attributes
                    wforms_ = [wform]
                    wform_ = wform.replace('ё', 'е')
                    if wform_ != wform:
                        wforms_.append(wform_)
                        nyo += 1
                    for wform in wforms_:
                        if lemma.islower():
                            wform = wform.lower()
                        wform_id = self._wforms_id.get(wform)
                        if wform_id is None:
                            wform_id = len(self._wforms)
                            self._wforms.append(wform)
                            self._wforms_id[wform] = wform_id
                        lemma_id = self._lemmata_id.get(lemma)
                        if lemma_id is None:
                            lemma_id = len(self._lemmata)
                            self._lemmata.append(lemma)
                            self._lemmata_id[lemma] = lemma_id
                        tag_id = self._tags_id.get(tag)
                        if tag_id is None:
                            tag_id = len(self._tags)
                            self._tags.append(tag)
                            self._tags_id[tag] = tag_id

                        self._wform_tag_cnts[wform_id][tag_id][lemma_id] = \
                            self._wform_tag_cnts.setdefault(wform_id, {}) \
                                                .setdefault(tag_id, {}) \
                                                .get(lemma_id, 0) + 1
                        self._lemma_tag_cnts[lemma_id][tag_id] = \
                            self._lemma_tag_cnts.setdefault(lemma_id, {}) \
                                                .get(tag_id, 0) + 1

                        wform_cnts_ = self._wform_feat_cnts \
                                          .setdefault(wform_id, {}) \
                                          .setdefault(tag_id, {}) \
                                          .setdefault(lemma_id, {})
                        lemma_cnts_ = self._lemma_feat_cnts \
                                          .setdefault(lemma_id, {}) \
                                          .setdefault(tag_id, {})

                        for feat, val in feats.items():
                            feat_id = self._feats_id.get(feat)
                            val_id = 1
                            if feat_id is None:
                                feat_id = len(self._feats)
                                self._feats.append(feat)
                                self._feat_vals.append(['_', val])
                                self._feats_id[feat] = feat_id
                                self._feat_vals_id.append({'_': 0,
                                                           val: val_id})
                            else:
                                vals = self._feat_vals[feat_id]
                                vals_id = self._feat_vals_id[feat_id]
                                val_id = vals_id.get(val)
                                if val_id is None:
                                    val_id = len(vals)
                                    vals.append(val)
                                    vals_id[val] = val_id
                            wform_cnts_[feat_id][val_id] = \
                                wform_cnts_.setdefault(feat_id, {}) \
                                           .get(val_id, 0) + 1
                            lemma_cnts_[feat_id][val_id] = \
                                lemma_cnts_.setdefault(feat_id, {}) \
                                           .get(val_id, 0) + 1
                elif tag is not None:
                    tag_id = self._tags_id.get(tag)
                    if tag_id is None:
                        tag_id = len(self._tags)
                        self._tags.append(tag)
                        self._tags_id[tag] = tag_id
                    for feat, val in feats.items():
                        feat_id = self._feats_id.get(feat)
                        val_id = 1
                        if feat_id is None:
                            feat_id = len(self._feats)
                            self._feats.append(feat)
                            self._feat_vals.append(['_', val])
                            self._feats_id[feat] = feat_id
                            self._feat_vals_id.append({'_': 0,
                                                       val: val_id})
                        else:
                            vals = self._feat_vals[feat_id]
                            vals_id = self._feat_vals_id[feat_id]
                            val_id = vals_id.get(val)
                            if val_id is None:
                                val_id = len(vals)
                                vals.append(val)
                                vals_id[val] = val_id

        if log_file:
            sent_no += 1
            print_progress(sent_no,
                           end_value=corpus_len if corpus_len else 0,
                           step=progress_step, file=log_file)
            print(('done: {} sentences, {} acceptable tokens '
                   '(plus {} for YO letters)')
                      .format(sent_no, ntoken, nyo),
                  file=log_file)

    def fit(self, cnt_thresh=None, ambiguity_thresh=None, log_file=LOG_FILE):
        """Gather additional statictics from corups information.

        :type cnt_thresh: int
        :type ambiguity_thresh: float
        If any wform was meet in corpus at least *cnt_thresh* times and it was
        tagged by the same label at least in *ambiguity_thresh* * 100% cases
        then that label will mark as trusted for that wform.

        :param log_file: stream for info messages
        :type file
        """
        if cnt_thresh is None:
            cnt_thresh = self._cnt_thresh
        else:
            self._cnt_thresh = cnt_thresh
        if ambiguity_thresh is None:
            ambiguity_thresh = self._ambiguity_thresh
        else:
            self._ambiguity_thresh = ambiguity_thresh

        if log_file:
            print('Fit corpus dict...', end=' ', file=log_file)
            log_file.flush()

        tag_id_cnts = {}
        total_cnt = 0

        self._most_probable_tags = {}
        for wform_id, item in self._wform_tag_cnts.items():
            tag_cnts = {x: sum(y.values()) for x, y in item.items()}
            for tag_id, cnt in tag_cnts.items():
                tag_id_cnts[tag_id] = tag_id_cnts.get(tag_id, 0) + cnt
                total_cnt += cnt
            tag_id, cnt = max(tag_cnts.items(), key=itemgetter(1))
            n = sum(tag_cnts.values())
            # Don't add rare wforms to the tag dictionary
            # Only add quite unambiguous wforms
            if n >= cnt_thresh and cnt / n >= ambiguity_thresh:
                self._most_probable_tags[wform_id] = tag_id

        self._tags_freq = [(self._tags[x], y, y / total_cnt)
                               for x, y in tag_id_cnts.items()]
        self._tags_freq.sort(key=lambda x: (x[1], x[0]), reverse=True)
        #self._most_common_tag = self._tags[
        #    max(tag_id_cnts.keys(), key=lambda x: (tag_id_cnts[x], x))
        #]
        if self._tags_freq:
            self._most_common_tag = self._tags_freq[0][0] 

        self._common_endings = eds = {}
        for wform_id, item in self._wform_tag_cnts.items():
            for tag_id, item in item.items():
                for lemma_id, cnt in item.items():
                    wform = self._wforms[wform_id]
                    lemma = self._lemmata[lemma_id]
                    if wform.isalpha() and lemma.isalpha():
                        wop, wcp, wed, lop, lcp, led = \
                            find_affixes(wform, lemma, lower=True)
                        if wcp and wop == lop:
                            for i in range(len(wcp) + 1):
                                wed_ = wcp[i:] + wed
                                led_ = lcp[i:] + led
                                eds[tag_id][wed_][led_] = \
                                    eds.setdefault(tag_id, {}) \
                                       .setdefault(wed_, {}) \
                                       .get(led_, 0) + 1
        for _, items in eds.items():
            for wed, led_cnts in items.items():
                items[wed] = sorted(led_cnts.items(),
                                    # x[0] for stability
                                    key=lambda x: (x[1], x[0]), reverse=True)

        # _capitalized_tags: Tags with mostly capitalized wforms
        tag_lower_cnts, tag_upper_cnts = {}, {}
        for lemma_id, tag_cnts in self._lemma_tag_cnts.items():
            lemma = self._lemmata[lemma_id]
            if lemma.isalpha():
                islower = lemma.islower()
                for tag_id, cnt in tag_cnts.items():
                    if islower:
                        tag_lower_cnts[tag_id] = \
                            tag_lower_cnts.get(tag_id, 0) + 1
                    else:
                        tag_upper_cnts[tag_id] = \
                            tag_upper_cnts.get(tag_id, 0) + 1
        self._capitalized_tags = set(
            x for x in range(len(self._tags))
                if tag_upper_cnts.get(x, 0) > tag_lower_cnts.get(x, 0))

        tag_feats = self._tag_feats = [set() for _ in range(len(self._tags))]
        feat_val_id_cnts            = [{}    for _ in range(len(self._tags))]
        for wform_id, item in self._wform_feat_cnts.items():
            for tag_id, item in item.items():
                for lemma_id, item in item.items():
                    for feat_id, item in item.items():
                        tag_feats[tag_id].add(feat_id)
                        for val_id, cnt in item.items():
                            feat_val_id_cnts[tag_id][feat_id][val_id] = \
                                feat_val_id_cnts[tag_id].setdefault(feat_id,
                                                                    {}) \
                                                        .get(val_id, 0) + cnt

        for tag_id, item in enumerate(feat_val_id_cnts):
            tag = self._tags[tag_id]
            total_cnt = sum(x for x in item.values() for x in x.values())
            feats_freq = self._feats_freq[tag] = []
            feat_vals = self._feat_vals_freq[tag] = {}
            for feat_id, item in item.items():
                feat = self._feats[feat_id]
                vals = self._feat_vals[feat_id]
                total_cnt2 = sum(item.values())
                feats_freq.append((feat, total_cnt2 / total_cnt))
                feat_vals_freq = feat_vals[feat] = []
                for val_id, cnt in item.items():
                    val = vals[val_id]
                    feat_vals_freq.append((val, cnt, cnt / total_cnt2))
                feat_vals_freq.sort(key=lambda x: (x[1], x[0]), reverse=True)
            feats_freq.sort(key=lambda x: (x[1], x[0]), reverse=True)

        self._most_probable_wform_feats = {}
        wtl_cnts = self._wform_tag_cnts
            # {wform_id: {tag_id: {lemma_id: cnt}}}
        for wform_id, item in self._wform_feat_cnts.items():  # {wform_id:
                         # {tag_id: {lemma_id: {feat_id: {val_id: cnt}}}}}
            tl_cnts = wtl_cnts[wform_id]  # {tag_id: {lemma_id: cnt}}
            feat_cnts = {}
            for tag_id, item in item.items():  # {tag_id:
                  # {lemma_id: {feat_id: {val_id: cnt}}}}
                l_cnts = tl_cnts[tag_id]  # {lemma_id: cnt}
                for lemma_id, item in item.items():  # {lemma_id: 
                                      # {feat_id: {val_id: cnt}}}
                    all_feats = set(tag_feats[tag_id])
                    _cnts = l_cnts[lemma_id]  # cnt
                    for feat_id, item in item.items():  # {feat_id: 
                                                   # {val_id: cnt}}
                        cnts = 0
                        all_feats.remove(feat_id)
                        for val_id, cnt in item.items():  # {val_id: cnt}
                            cnts += cnt
                            feat_cnts[feat_id][val_id] = \
                                feat_cnts.setdefault(feat_id, {}) \
                                         .get(val_id, 0) + cnt
                        if _cnts > cnts:
                            feat_cnts[feat_id][0] = \
                                feat_cnts.setdefault(feat_id, {}) \
                                         .get(0, 0) + _cnts - cnts
                    for feat_id in all_feats:
                        feat_cnts[feat_id][0] = \
                            feat_cnts.setdefault(feat_id, {}) \
                                     .get(0, 0) + _cnts
            for feat_id, val_cnts in feat_cnts.items():
                val_id, cnt = max(val_cnts.items(), key=itemgetter(1))
                n = sum(val_cnts.values())
                # Don't add rare wforms to the feat dictionary
                # Only add quite unambiguous wforms
                if n >= cnt_thresh and cnt / n >= ambiguity_thresh:
                    self._most_probable_wform_feats \
                        .setdefault(wform_id, {})[feat_id] = val_id

        self._most_probable_lemma_feats = {}
        lt_cnts = self._lemma_tag_cnts
            # {lemma_id: {tag_id: cnt}}
        for lemma_id, item in self._lemma_feat_cnts.items():  # {lemma_id:
                                     # {tag_id: {feat_id: {val_id: cnt}}}}
            t_cnts = lt_cnts[lemma_id]  # {tag_id: cnt}
            feat_cnts = {}
            for tag_id, item in item.items():  # {tag_id:
                              # {feat_id: {val_id: cnt}}}
                all_feats = set(tag_feats[tag_id])
                _cnts = t_cnts[tag_id]  # cnt
                for feat_id, item in item.items():  # {feat_id: 
                                               # {val_id: cnt}}
                    cnts = 0
                    all_feats.remove(feat_id)
                    for val_id, cnt in item.items():  # {val_id: cnt}
                        cnts += cnt
                        feat_cnts[feat_id][val_id] = \
                            feat_cnts.setdefault(feat_id, {}) \
                                     .get(val_id, 0) + cnt
                    if _cnts > cnts:
                        feat_cnts[feat_id][0] = \
                            feat_cnts.setdefault(feat_id, {}) \
                                     .get(0, 0) + _cnts - cnts
                for feat_id in all_feats:
                    feat_cnts[feat_id][0] = \
                        feat_cnts.setdefault(feat_id, {}) \
                                 .get(0, 0) + _cnts
            for feat_id, val_cnts in feat_cnts.items():
                val_id, cnt = max(val_cnts.items(), key=itemgetter(1))
                n = sum(val_cnts.values())
                # Don't add rare lemmata to the feat dictionary
                # Only add quite unambiguous lemmata
                if n >= cnt_thresh and cnt / n >= ambiguity_thresh:
                    self._most_probable_lemma_feats \
                        .setdefault(lemma_id, {})[feat_id] = val_id

        if log_file:
            print('done.', file=log_file)

    def get_tags(self):
        """Return a set of all known tag labels.
        
        :rtype: set(str)
        """
        return set(self._tags)
    
    def get_feats(self):
        """Return a dict of all known feats with their possible value labels.

        :rtype: dict(str: set(str))
        """
        return {feat: set(val for val in self._feat_vals[i])
                          for i, feat in enumerate(self._feats)}

    def get_tag_feats(self, tag):
        """Return a set of all known feat labels for a given tag.
        
        :rtype: set(str)
        """
        tag_id = self._tags_id.get(tag)
        assert tag_id is not None, 'ERROR: Unknown tag specified'
        return set(self._feat_vals[feat_id] \
                       for feat_id in self._tag_feats[tag_id])

    def get_tags_freq(self):
        """Return tags ordered by frequency.
        
        :rtype: [(tag, count, tag_freq)]
        """
        return self._tags_freq[:]
    
    def get_feats_freq(self, tag):
        """Return feats ordered by frequency for a given *tag*.
        
        :rtype: [(feat, count, feat_freq)]
        """
        return self._feats_freq[tag][:]
    
    def get_feat_vals_freq(self, tag, feat):
        """Return feat values ordered by frequency for a given *tag* and
        *feat*.
        
        :rtype: [(val, count, val_freq)]
        """
        return self._feat_vals_freq[tag].get(feat, [])[:]

    def wform_isknown(self, wform, tag=None):
        res = self._wforms_id.get(wform)
        if res is None:
            res = self._wforms_id.get(wform.lower())
        if res is None:
            res = self._lemmata_id.get(wform)
            if res is None:
                res = self._lemmata_id.get(wform.lower())
            if res is not None and tag:
                res = self._lemma_tag_cnts[res].get(self._tags_id[tag])
        elif tag:
            res = self._wform_tag_cnts[res].get(self._tags_id[tag])
        return res is not None

    def most_common_tag(self):
        """Return most common tag for the whole corpus"""
        return self._most_common_tag

    def predict_tag(self, wform, isfirst=False, cnt_thresh=None):
        """If the *wform* has a trusted tag then return that tag with
        a relevance coef equals to 1. Elsewise, we choose the most common tag
        for that *wform* and calculate some empirical value as a relevance
        coef.

        The relevance coef may be used to improve an alternative tag
        prediction algorithm.

        :param cnt_thresh: if the *wform* was meet in corpus less than
                           *cnt_thresh* times then the relevance coef will be
                           discounted by (count / cnt_thresh)
        :type cnt_thresh: int
        :return: tag predicted and relevance coef
        :rtype: tuple(str, float)

        If the *wform* is not known then return (None, None)"""
        if cnt_thresh is None:
            cnt_thresh = self._cnt_thresh

        tag, coef = None, None
        wform_id = self._wforms_id.get(wform)
        wform_id2 = None
        if wform_id is None:
            wform_id = self._wforms_id.get(wform.lower())
        elif isfirst and wform.istitle():
            wform_id2 = self._wforms_id.get(wform.lower())
        if wform_id is not None:
            if wform_id2 is None:
                tag_id = self._most_probable_tags.get(wform_id)
                if tag_id is not None:
                    tag, coef = self._tags[tag_id], 1.
            if tag is None:
                tag_cnts = {
                    x: sum(y.values())
                        for x, y in self._wform_tag_cnts[wform_id].items()
                }
                if wform_id2 is not None:
                    for x, y in [
                        (x, sum(y.values()))
                            for x, y in self._wform_tag_cnts[wform_id2].items()
                    ]:
                        tag_cnts[x] = tag_cnts.get(x, 0) + y
                #n = sum(tag_cnts.values())
                # x[0] for stability
                tag_id, cnt = max(tag_cnts.items(), key=lambda x: (x[1], x[0]))
                del tag_cnts[tag_id]
                cnt2 = max(tag_cnts.values()) if tag_cnts else 0
                tag = self._tags[tag_id]
                coef = (cnt - cnt2) * min((cnt - cnt2) / cnt_thresh, 1.) / cnt
                #if isfirst and self._wforms[wform_id].istitle():
                #    tag2, coef2 = self.predict_tag(wform.lower())
                #    if coef2 and coef2 > coef:
                #        tag, coef = tag2, coef2
        return tag, coef

    def predict_lemma(self, wform, tag, isfirst=False, cnt_thresh=None):
        """Choose the most common lemma for the *wform* and *tag* and calculate
        some empirical value as a relevance coef.

        The relevance coef may be used to improve an alternative lemma
        prediction algorithm.

        :isfirst: True if the *wform* is first in a sequence
        :param cnt_thresh: if the *wform* was meet in corpus less than
                           *cnt_thresh* times then the relevance coef will be
                           discounted by (count / cnt_thresh)
        :type cnt_thresh: int
        :return: lemma chosen and relevance coef
        :rtype: tuple(str, float)
        """
        tag_id = self._tags_id.get(tag)
        assert tag_id is not None, 'ERROR: Unknown tag specified'

        if cnt_thresh is None:
            cnt_thresh = self._cnt_thresh

        lemma, coef = None, None
        if wform.isalpha():
            lemma_cnts = None
            wform_hascaps = not wform.islower()

            # Trying to find wform in a dict
            wform_id = self._wforms_id.get(wform)
            if wform_id is not None:
                lemma_cnts = self._wform_tag_cnts[wform_id].get(tag_id)
                if not lemma_cnts:
                    wform_id = None
            if wform_id is None and wform_hascaps:
                wform_id = self._wforms_id.get(wform.lower())
                if wform_id is not None:
                    lemma_cnts = self._wform_tag_cnts[wform_id].get(tag_id)

            # Wform is in a dict, so lemma is in a dict, too
            if lemma_cnts:
                lemma_cnts = sorted(lemma_cnts.items(),
                                    # x[0] for stability
                                    key=lambda x: (x[1], x[0]), reverse=True)
                lemma_id, cnt = lemma_cnts[0]
                cnt2 = lemma_cnts[1][1] if len(lemma_cnts) > 1 else 0
                lemma = self._lemmata[lemma_id]
                # Strong sorcery. Don't think about it.
                coef = (cnt - cnt2) * min((cnt - cnt2) / cnt_thresh, 1.) / cnt

            # Wform is not in a dict
            else:
                # Known endings for a given tag
                eds = self._common_endings.get(tag_id)
                if eds:
                    # Search first known lemma amongst generated ones sorted by
                    # frequency and length. In addition, keep in mind the first
                    # generated lemma.
                    known_lemma = gen_lemma = None
                    for i in range(len(wform)):
                        # Check all known lemma endings for a given wform
                        # ending
                        eds_ = eds.get(wform[i:])
                        if eds_:
                            # eds_ - list of tuples sorted by frequency
                            for ed, _ in eds_:
                                lemma_ = wform[:i] + ed
                                # If lemma is in a dict, we've found it.
                                lemma_id = self._lemmata_id.get(lemma_)
                                if lemma_id is not None \
                               and self._lemma_tag_cnts[lemma_id].get(tag_id):
                                    known_lemma = lemma_
                                    break
                                # Save the first generated lemma
                                if not gen_lemma:
                                    gen_lemma = lemma_
                            else:
                                continue
                            break
                    # If known lemma has not found and wform is not lower, do
                    # all the same for its lower form
                    if not known_lemma and wform_hascaps:
                        wform_lower = wform.lower()
                        for i in range(len(wform)):
                            eds_ = eds.get(wform_lower[i:])
                            if eds_:
                                for ed, _ in eds_:
                                    lemma_ = wform_lower[:i] + ed
                                    lemma_id = self._lemmata_id.get(lemma_)
                                    if lemma_id is not None \
                                   and self._lemma_tag_cnts[lemma_id].get(tag_id):
                                        known_lemma = lemma_
                                        break
                                    if not gen_lemma:
                                        gen_lemma = lemma_
                                        ## Has no effect:
                                        #gen_lemma = lemma_ \
                                        #    if not isfirst \
                                        #    or tag_id \
                                        #        not in self._capitalized_tags \
                                        #    else wform[:i] + ed
                                else:
                                    continue
                                break
                    if known_lemma:
                        lemma, coef = known_lemma, .9
                    elif gen_lemma:
                        lemma, coef = gen_lemma, 0

        # If lemma is not found after all, set lemma = wform
        if not lemma:
            lemma, coef = wform, 0
        return lemma, coef

    def predict_feat(self, feat, wform, lemma, tag, cnt_thresh=None):
        """Choose the most common *feat* for the *wform*, *tag*, and *lemma*
        and calculate some empirical value as a relevance coef.

        The relevance coef may be used to improve an alternative feats
        prediction algorithm.

        :param cnt_thresh: if the *wform* was meet in corpus less than
                           *cnt_thresh* times then the relevance coef will be
                           discounted by (count / cnt_thresh)
        :type cnt_thresh: int
        :return: feat predicted and relevance coef
        :rtype: tuple(str, float)

        If the *wform* is not known then return (None, None)"""
        feat_id = self._feats_id.get(feat)
        assert feat_id is not None, 'ERROR: Unknown feat specified'
        tag_id = self._tags_id.get(tag)
        assert tag_id is not None, 'ERROR: Unknown tag specified'

        if cnt_thresh is None:
            cnt_thresh = self._cnt_thresh

        val, coef = None, None
        if feat_id not in self._tag_feats[tag_id]:
            val, coef = None, 1.
        else:
            wform_id = self._wforms_id.get(wform)
            if wform_id is None:
                wform_id = self._wforms_id.get(wform.lower())
            if wform_id is not None:
                val_id = self._most_probable_wform_feats.get(wform_id, {}).get(
                    feat_id, self._most_probable_lemma_feats.get(
                        self._lemmata_id.get(lemma), {}
                    ).get(feat_id)
                )
                if val_id is not None:
                    val, coef = self._feat_vals[feat_id][val_id], 1.
                else:
                    feat_cnts = self._wform_feat_cnts[wform_id] \
                                    .get(tag_id, {}) \
                                    .get(self._lemmata_id.get(lemma))
                        # {wform_id: {tag_id: {lemma_id:
                        #    {feat_id: {val_id: cnt}}}}}
                    tag_cnt = sum(
                        self._wform_tag_cnts[wform_id].get(tag_id, {}).values()
                    )
                        # {wform_id: {tag_id:
                        #   {lemma_id: cnt}}}
                    if feat_cnts:
                        val_cnts = dict(feat_cnts.get(feat_id, {}))  # {feat_id:
                        #                                         {val_id: cnt}}
                        # add '_' with count = count(tag) - count(feat)
                        val_cnts.update({0: tag_cnt - sum(val_cnts.values())})
                        # x[0] for stability
                        val_id, cnt = max(
                            val_cnts.items(), key=lambda x: (x[1], x[0])
                        )
                        del val_cnts[val_id]
                        cnt2 = max(val_cnts.values()) if val_cnts else 0
                        val = self._feat_vals[feat_id][val_id]
                        coef = (cnt - cnt2) \
                             * min((cnt - cnt2) / cnt_thresh, 1.) \
                             / cnt
                    else:  # feat_cnts == {}
                        val = self._feat_vals[feat_id][0]  # '_'
                        coef = min(tag_cnt / cnt_thresh, 1.)
        return val, coef
