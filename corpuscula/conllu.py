# -*- coding: utf-8 -*-
# Corpuscula project: CoNLL-U support
#
# Copyright (C) 2019-present by Sergei Ternovykh
# License: BSD, see LICENSE for details
"""
Full CoNLL-U and CoNLL-U Plus formats support.
"""
from collections import OrderedDict
from difflib import SequenceMatcher
from io import BufferedReader
import os
import pickle
import sys

from corpuscula.utils import LOG_FILE, print_progress


def id_to_numeric(id_):
    # there will be ValueError if id is incorrect
    return None if id_ is None else \
           int(id_) if id_.isdecimal() else \
           float(id_)


class Conllu:
    """Full CoNLL-U and CoNLL-U Plus formats support"""

    STD_COLUMNS = ['ID', 'FORM', 'LEMMA', 'UPOS', 'XPOS',
                   'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC']

    def __new__(cls):
        raise NotImplementedError('This class has only static methods')

    @staticmethod
    def fix(corpus, split_multi=False, adjust_for_speech=False):
        """Fix Parsed CoNLL-U structure of *corpus* (renew token ids, generate
        sentence ids and text if they are not present in metadata, etc.)

        :param split_multi: if True then wforms with spaces will be processed
                            as multiword tokens
        :param adjust_for_speech: if True, remove all non alphanumeric tokens
                                  and convert all words to lower case
        :rtype: iter
        """
        for sent_no, sentence in enumerate(corpus):
            sentence, sentence_meta = \
                sentence if isinstance(sentence, tuple) else \
                (sentence, OrderedDict())

            tokens = []
            id_, sub_id = 0, 0
            multi_token, last_old_id = None, None
            for token in sentence:
                if adjust_for_speech:
                    wform = token['FORM']
                    if wform and any(x.isalnum() for x in wform):
                        token['FORM'] = wform.lower()
                        if token['LEMMA']:
                            token['LEMMA'] = token['LEMMA'].lower()
                    elif wform is not None:
                        continue
                tokens.append(token)
                columns = token.keys()
                if 'ID' in token and 'FORM' in columns:
                    old_id = token['ID'] or ''
                    if '.' in old_id:
                        sub_id += 1
                        token['ID'] = str(id_) + '.' + str(sub_id)
                    elif multi_token:
                        #if '.' in old_id:
                        #    sub_id += 1
                        #    token['ID'] = str(id_) + '.' + str(sub_id)
                        #else:
                        id_ += 1
                        sub_id = 0
                        token['ID'] = str(id_)
                        if old_id == last_old_id:
                            multi_token['ID'] += '-' + str(id_)
                            multi_token = None
                    else:
                        wform = token['FORM']
                        if wform:
                            id_ += 1
                            sub_id = 0
                            token['ID'] = str(id_)
                            dash_pos = old_id.rfind('-')
                            if dash_pos > 0:
                                multi_token = token
                                last_old_id = old_id[dash_pos + 1:]
                                id_ -= 1
                            else:
                                wforms = wform.strip().split()
                                if split_multi and len(wforms) > 1:
                                    assert not any(
                                        token[x] for x in token.keys()
                                                     if x not in [
                                                         'ID', 'FORM', 'MISC'
                                                     ]
                                    ), 'ERROR: Fix of CoNLL-U structure ' \
                                       'with split_multi=True can be made ' \
                                       'before any tagging'
                                    for id_, wform in enumerate(wforms,
                                                                start=id_):
                                        token_ = {}
                                        for column in columns:
                                            token_[column] = \
                                                str(id_) \
                                                    if column == 'ID' else \
                                                wform \
                                                    if column == 'FORM' else \
                                                OrderedDict() if column in [
                                                    'FEATS', 'MISC'
                                                ] else \
                                                None
                                        tokens.append(token_)
                                    token['ID'] += '-' + str(id_)
                        else:
                            sub_id += 1
                            token['ID'] = str(id_) + '.' + str(sub_id)
            sentence = tokens
            if not sentence:
                vals = {}
                for column in columns:
                    vals[column] = \
                        '0.1' if column == 'ID' else \
                        OrderedDict() if column in ['FEATS', 'MISC'] else \
                        None
                sentence = [vals]

            if 'sent_id' not in sentence_meta:
                sentence_meta['sent_id'] = str(sent_no + 1)
                sentence_meta.move_to_end('sent_id', last=False)
            if 'text' not in sentence_meta:
                text = ''
                space_before = False
                ignore_upto = None
                for token in sentence:
                    id_, wform, misc = \
                        token['ID'], token['FORM'], token.get('MISC', {})
                    if ignore_upto:
                        if id_ == ignore_upto:
                            ignore_upto = None
                    elif '.' not in id_:
                        ids = id_.split('-')
                        if len(ids) == 2:
                            id_ = ignore_upto = ids[1]
                        if id_.isdigit():
                            if space_before:
                                text += ' '
                            text += wform
                    space_before = misc.get('SpaceAfter') != 'No'
                sentence_meta['text'] = text

            yield sentence, sentence_meta

    @classmethod
    def from_sentence(cls, wforms, columns=None):
        """Convert a list of wforms to Parsed CoNLL-U format.

        :param columns: list of column names. If None, standard CoNLL-U columns
                        are used
        :type columns: list(str)

        NB: If wform contains '\u00AD' character, it will be splitted by that
            character, and all it's parts except the last one will be saved
            with the "SpaceAfter=No" MISC attribute"""
        if columns is None:
            columns = cls.STD_COLUMNS
        sent = []
        for i, w in enumerate(wforms, start=1):
            wform = w
            while wform:
                pos = wform.find('\u00AD')
                if pos < 0:
                    w, wform = wform, ''
                else:
                    w, wform = wform[:pos], wform[pos + 1:]
                token = {}
                for column in columns:
                    token[column] = str(i) if column == 'ID' else \
                                    w if column == 'FORM' else \
                                    OrderedDict() if column in [
                                        'FEATS', 'MISC'
                                    ] else \
                                    None
                if wform and 'MISC' in columns:
                    token['MISC']['SpaceAfter'] = 'No'
                sent.append(token)
        return sent

    @classmethod
    def from_sentences(cls, sentences, split_multi=False,
                       adjust_for_speech=False, columns=None):
        """Convert a sequence of tokenized sentences to Parsed CoNLL-U format

        :param fix: fix CoNLL-U structure of after conversion
        :param split_multi: if True then wforms with spaces will be processed
                            as multiword tokens (used only with fix=True)
        :param adjust_for_speech: if yes, remove all non alphanumeric tokens
                                  and convert all words to lower case (used
                                  only with fix=True)
        :rtype: iter
        """
        yield from cls.fix((cls.from_sentence(s, columns=columns)
                               for s in sentences),
                           split_multi=split_multi,
                           adjust_for_speech=adjust_for_speech)

    @classmethod
    def load(cls, corpus, encoding='utf-8-sig', fix=True, split_multi=False,
             adjust_for_speech=False, log_file=LOG_FILE):
        """Load corpus in CoNLL-U format as sequence of Parsed CoNLL-U
        sentences. Each sentence returns as tuple of a list of tagged tokens
        and a dict of metadata that can be used to restore corpus back to
        CoNLL-U format.

        :param fix: fix CoNLL-U structure of after conversion
        :param split_multi: if True then wforms with spaces will be processed
                            as multiword tokens (used only with fix=True)
        :param adjust_for_speech: if yes, remove all non alphanumeric tokens
                                  and convert all words to lower case (used
                                  only with fix=True)
        :return: sentences in Parsed CoNLL-U format
        :rtype: sequence of tuple(list(dict(str: str|OrderedDict(str: str))),
                                  OrderedDict(str: str))

        NOTE: For CoNLL-U Plus format the field list must be specified in the
              first line of the *corpus* (in the meta variable
              "global.columns")"""
        if fix:
            yield from cls.fix(cls.load(corpus, encoding=encoding, fix=False,
                                        log_file=log_file),
                               split_multi=split_multi,
                               adjust_for_speech=adjust_for_speech)

        else:
            if isinstance(corpus, str):# and os.path.exists(corpus):
                corpus = open(corpus, mode='rt', encoding=encoding)

            if log_file:
                print('Load corpus', file=log_file)
            nsentence = ntoken = 0
            sentence = []
            sentence_meta = OrderedDict()
            columns = None
            sent_no = -1
            for line_no, line in enumerate(corpus):
                line = line.strip()
                if len(line) == 0:
                    if len(sentence) > 0 or len(sentence_meta) > 0:
                        if len(sentence) == 0:
                            if columns is None:
                                columns = cls.STD_COLUMNS
                            vals = {}
                            for column in columns:
                                vals[column] = \
                                    '0.1' if column == 'ID' else \
                                    OrderedDict() \
                                        if column in ['FEATS', 'MISC'] else \
                                    None
                            sentence = [vals]
                        yield sentence, sentence_meta
                        sent_no += 1
                        if log_file and not sent_no % 100:
                            print_progress(sent_no, end_value=None, step=1000,
                                           file=log_file)
                        nsentence += 1
                        ntoken += len(sentence)
                        sentence = []
                        sentence_meta = OrderedDict()
                elif line[0] == '#':
                    meta = tuple(x.strip() for x in line[1:].split('=', 1))
                    sentence_meta.update(
                        [meta if len(meta) > 1 else (meta[0], None)]
                    )
                    if columns is None and meta[0] == 'global.columns':
                        columns = meta[1].split()
                    else:
                        columns = cls.STD_COLUMNS
                else:
                    if columns is None:
                        columns = cls.STD_COLUMNS
                    columns_i = iter(columns)
                    vals = {}
                    for val in line.split('\t'):
                        column = next(columns_i)
                        if column in ['FEATS', 'MISC']:
                            try:
                                val = OrderedDict(
                                    () if val == '_' else
                                        or val.startswith ('_|') else
                                    [(k, v) for k, v in [
                                        t.split('=', 1) for t in val.split('|')
                                    ]])
                            except ValueError as e:
                                print('ERROR when loading Conllu (line {})'
                                          .format(line_no + 1), sys.stderr)
                                print(line, sys.stderr)
                                print(column, sys.stderr)
                                print(val, sys.stderr)
                                raise e
                        else:
                            if val == '_':
                                val = None
                            if val == '*' and column not in cls.STD_COLUMNS:
                                val = ''
                        vals[column] = val
                    sentence.append(vals)
            if sentence or sentence_meta:
                yield sentence, sentence_meta
                sent_no += 1
            if log_file and sent_no >= 0:
                print_progress(sent_no + 1, end_value=0, step=1000,
                               file=log_file)
                print('Corpus has been loaded: {} sentences, {} tokens'
                          .format(nsentence, ntoken),
                      file=log_file)

            if isinstance(corpus, BufferedReader):
                corpus.close()

    @classmethod
    def get_as_text(cls, corpus, fix=True, split_multi=False,
                    adjust_for_speech=False, log_file=LOG_FILE):
        """Convert a *corpus* in Parsed CoNLL-U format to text form.

        :rtype: iter(str)
        """
        if log_file:
            print('Save corpus', file=log_file)
        sent_no = -1
        for sent_no, sentence in enumerate(
            cls.fix(corpus, split_multi=split_multi,
                    adjust_for_speech=adjust_for_speech) if fix else
            corpus
        ):
            if log_file and not sent_no % 100:
                print_progress(sent_no, end_value=None, step=1000,
                               file=log_file)
            sentence, sentence_meta = \
                sentence if isinstance(sentence, tuple) else \
                (sentence, OrderedDict())

            columns, feats_idx, misc_idx = [None] * 3
            first_meta = []
            for meta, val in sentence_meta.items():
                if columns is None and meta == 'global.columns':
                    columns = val.split()
                    try:
                        feats_idx = columns.index('FEATS')
                    except ValueError:
                        pass
                    try:
                        misc_idx = columns.index('MISC')
                    except ValueError:
                        pass
                line = '# {}{}'.format(meta, ' = {}'.format(val)
                                                 if val is not None else
                                             '')
                if columns is None:
                    first_meta.append(line)
                else:
                    yield line + '\n'
            line = []
            for token in sentence:
                if columns is None:
                    columns = []
                    cols = set(token.keys())
                    for col in cls.STD_COLUMNS:
                        if col in cols:
                            if col == 'FEATS':
                                feats_idx = len(columns)
                            if col == 'MISC':
                                misc_idx = len(columns)
                            columns.append(col)
                            cols.remove(col)
                    if cols:
                        columns.extend(sorted(cols))
                        yield '# global.columns = ' + ' '.join(columns) + '\n'
                    if first_meta:
                        for line in first_meta:
                            yield line + '\n'
                line = ['_' if token[x] is None else
                        '*' if token[x] == ''
                           and x not in cls.STD_COLUMNS else
                        token[x] for x in columns]
                if feats_idx is not None:
                    feats = line[feats_idx]
                    line[feats_idx] = \
                        '|'.join('='.join((x, feats[x])) \
                                     for x in sorted(feats)) \
                                         if feats else \
                                 '_'
                if misc_idx is not None:
                    misc = line[misc_idx]
                    line[misc_idx] = \
                        '|'.join('='.join((x, misc[x])) \
                                     for x in sorted(misc)) \
                                         if misc else \
                                 '_'
                yield '\t'.join(line) + '\n'
            yield '\n'
        if log_file and sent_no >= 0:
            print_progress(sent_no + 1, end_value=0, step=1000,
                           file=log_file)
            print('Corpus has been saved', file=log_file)

    @classmethod
    def save(cls, corpus, file_path, **kwargs):
        """Save a *corpus* in Parsed CoNLL-U format to CoNLL-U file"""
        with open(file_path, mode='wt', encoding='utf-8') as f:
            for line in cls.get_as_text(corpus, **kwargs):
                print(line, end='', file=f)
