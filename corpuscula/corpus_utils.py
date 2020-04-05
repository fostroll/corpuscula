# -*- coding: utf-8 -*-
# Corpuscula project: Wrappers for known corpora
#
# Copyright (C) 2019-present by Sergei Ternovykh
# License: BSD, see LICENSE for details
"""
Tools for downloading and converting known corpora of Russian language.
Includes wrapper for corupses to simplify the further processing.
"""
from collections import OrderedDict
from html import unescape
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError

from .conllu import Conllu
from .utils import LOG_FILE, download_file, rmdir, read_bz2, read_rar, read_zip


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
_CFG_ROOT_DIR = 'ROOT_DIR'
def set_root_dir(root_dir):
    root_dir = root_dir.strip()
    cfg_path = os.path.join(Path.home(), '.rumor')
    cfg = ["# Config file for RuMor project. Don't change it manually."]
    isdone = False
    if os.path.isfile(cfg_path):
        with open(cfg_path, 'rt', encoding='utf-8') as f:
            for line in f:
                try:
                    var, val = line.split('\t', maxsplit=1)
                    if var == _CFG_ROOT_DIR:
                        if not isdone:
                            val = root_dir
                            isdone = True
                        else:
                            continue
                    cfg.append('\t'.join((var, val.strip())))
                except ValueError:
                    pass
    if not isdone:
        cfg.append('\t'.join((_CFG_ROOT_DIR, root_dir)))
    with open(cfg_path, 'wt', encoding='utf-8') as f:
        for line in cfg:
            print(line, file=f)

def get_root_dir():
    cfg_path = os.path.join(Path.home(), '.rumor')
    res = ROOT_DIR
    with open(cfg_path, 'rt', encoding='utf-8') as f:
        for line in f:
            try:
                var, val = line.split('\t', maxsplit=1)
                if var == _CFG_ROOT_DIR:
                    res = val.strip()
                    break
            except ValueError:
                pass
    return res

CORPUS_DNAME = 'corpus'
def download_corpus(name, url, dname=None, root_dir=None, fname=None,
                    **kwargs):
    """Download a corpus *name* from *url*. The corpus will be stored inside
    the project corpus storage in the directory *dname* with the file name
    *fname*.

    If *dname* is None, corpus will be downloaded right in the root
    of the storage.

    If *fname is None, the name of the file will be copied from the *url*

    :param root_dir: path to the root storage. If None, default value will
                     be used
    :type root_dir: str

    Also, the function receives other parameters that fit for
    ``.utils.download_file()`` method"""
    dpath = os.path.join(root_dir if root_dir else get_root_dir(),
                         CORPUS_DNAME,
                         dname if dname is not None else '')
    
    return download_file(url, dpath=dpath, fname=fname,
                         log_msg='Downloading {}'.format(name), **kwargs)

def remove_corpus(dname, root_dir=None):
    """Remove a directory *dname* from the project corpus storage.

    WARNING: All files in the directory will be removed.

    :param root_dir: path to the root storage. If None, default value will
                     be used
    :type root_dir: str

    If *dname* is None, the corpus storage will be totally cleaned. All
    downloaded corpora will be removed"""
    dpath = os.path.join(root_dir if root_dir else get_root_dir(),
                         CORPUS_DNAME,
                         dname if dname is not None else '')
    try:
        rmdir(dpath)
    except FileNotFoundError:
        pass
    try:
        os.rmdir(os.path.join(root_dir if root_dir else get_root_dir(),
                              CORPUS_DNAME))
    except OSError:
        pass

def get_corpus_fpath(dname=None, root_dir=None, fname=None, url=None):
    """Return full path for file *fname* from project corpus storage directory
    *dname*. If *fname* is None, the name of the file will be copied from the
    *url*. No cheking of the file existance is made.

    :param root_dir: path to the root storage. If None, default value will
                     be used
    :type root_dir: str
    """
    assert fname is not None or url is not None, \
        '*fname* or *url* must be not None'
    dpath = os.path.join(root_dir if root_dir else get_root_dir(),
                         CORPUS_DNAME,
                         dname if dname is not None else '')
    fpath = os.path.join(dpath, fname if fname else
                                re.sub('^.+/', '', url))
    return fpath

def _get_ud_train_name(file_list):
    return next((x for x in file_list if x.endswith('train.conllu')), None)

def _get_ud_dev_name(file_list):
    return next((x for x in file_list if x.endswith('dev.conllu')), None)

def _get_ud_test_name(file_list):
    return next((x for x in file_list if x.endswith('test.conllu')), None)

UD = 'UniversalDependencies'
UD_URL = 'https://api.github.com/repos/UniversalDependencies/{}/contents/'
UD_DNAME = '_UD'
def download_ud(corpus_name, root_dir=None, overwrite=True):
    """Download a corpus ``corpus_name`` from Universal Dependencies.

    :param corpus_name: name of the corpus as it specified on the Universal
                        Dependencies' site
    :type corpus_name: str
    :param root_dir: path to the root storage. If None, default value will
                     be used
    :type root_dir: str
    :param overwrite: False means do not download the corpus if it's already
                      kept in the corpus storage
    """
    fpaths = []
    dpath = os.path.join(root_dir if root_dir else get_root_dir(),
                         CORPUS_DNAME, UD_DNAME)
    fcont = corpus_name + '.contents'
    try:
        download_file(UD_URL.format(corpus_name),
                      dpath=dpath, fname=fcont, overwrite=overwrite,
                      log_msg='Downloading {}/{} contents'
                                  .format(UD, corpus_name))
    except HTTPError as e:
        if e.code == 404:
            print('Corpus {} has not found in Universal Dependencies'
                      .format(corpus_name))
            fpaths = None
        else:
            raise e
    if fpaths is not None:
        train, dev, test = [None] * 3
        fcont = os.path.join(dpath, fcont)
        with open(fcont, 'rt', encoding='utf-8') as f:
            cont = json.loads(f.read())
            urls = [o.get('download_url') for o in cont]
            train, dev, test = _get_ud_train_name(urls), \
                                 _get_ud_dev_name(urls), \
                                _get_ud_test_name(urls)
            dpath = os.path.join(dpath, corpus_name)
            if train:
                fpaths.append(
                    download_corpus('{}/{}:train'.format(UD, corpus_name),
                                    train, dname=dpath, root_dir='',
                                    overwrite=overwrite))
            if dev:
                fpaths.append(
                    download_corpus('{}/{}:dev'.format(UD, corpus_name),
                                    dev, dname=dpath, root_dir='',
                                    overwrite=overwrite))
            if test:
                fpaths.append(
                    download_corpus('{}/{}:test'.format(UD, corpus_name),
                                    test, dname=dpath, root_dir='',
                                    overwrite=overwrite))
        os.remove(fcont)
    return fpaths

def remove_ud(corpus_name, root_dir=None):
    """Remove a corpus ``corpus_name`` of Universal Dependencies.

    :param corpus_name: name of the corpus as it specified on the Universal
                        Dependencies' site
    :type corpus_name: str
    :param root_dir: path to the root storage. If None, default value will
                     be used
    :type root_dir: str
    """
    remove_corpus(os.path.join(UD_DNAME, corpus_name), root_dir=root_dir)

def get_ud_train_path(corpus_name, root_dir=None):
    """Return a name of the train corpus of a corpus ``corpus_name`` of 
    Universal Dependencies"""
    dpath = os.path.join(root_dir if root_dir else get_root_dir(),
                         CORPUS_DNAME, UD_DNAME, corpus_name)
    fname = _get_ud_train_name(os.listdir(dpath))
    return os.path.join(dpath, fname) if fname else None

def get_ud_dev_path(corpus_name, root_dir=None):
    """Return a name of the dev corpus of a corpus ``corpus_name`` of 
    Universal Dependencies"""
    dpath = os.path.join(root_dir if root_dir else get_root_dir(),
                         CORPUS_DNAME, UD_DNAME, corpus_name)
    fname = _get_ud_dev_name(os.listdir(dpath))
    return os.path.join(dpath, fname) if fname else None

def get_ud_test_path(corpus_name, root_dir=None):
    """Return a name of the test corpus of a corpus ``corpus_name`` of 
    Universal Dependencies"""
    dpath = os.path.join(root_dir if root_dir else get_root_dir(),
                         CORPUS_DNAME, UD_DNAME, corpus_name)
    fname = _get_ud_test_name(os.listdir(dpath))
    return os.path.join(dpath, fname) if fname else None

GICR = 'GICR'
GICR_URL = 'https://github.com/dialogue-evaluation/morphoRuEval-2017/raw/master/GIKRYA_texts_new.zip'
GICR_DNAME = 'gicr'
def download_gicr(root_dir=None, overwrite=True):
    """Download the corpus GICR.
    
    :param root_dir: path to the root storage. If None, default value will
                     be used
    :type root_dir: str
    :param overwrite: False means do not download the corpus if it's already
                      kept in the corpus storage
    """
    return download_corpus(GICR, GICR_URL, dname=GICR_DNAME, root_dir=root_dir,
                           overwrite=overwrite, file_noless=8000000)

def remove_gicr(root_dir=None):
    """Remove the corpus GICR.

    :param root_dir: path to the root storage. If None, default value will
                     be used
    :type root_dir: str
    """
    remove_corpus(GICR_DNAME, root_dir=root_dir)

OPENCORPORA = 'OpenCorpora'
OPENCORPORA_URL = 'http://opencorpora.org/files/export/annot/annot.opcorpora.xml.bz2'
OPENCORPORA_NOAMB_URL = 'http://opencorpora.org/files/export/annot/annot.opcorpora.no_ambig.xml.bz2'
OPENCORPORA_NOAMB_NOUNKN_URL = 'http://opencorpora.org/files/export/annot/annot.opcorpora.no_ambig_strict.xml.bz2'
OPENCORPORA_DICT_URL = 'http://opencorpora.org/files/export/dict/dict.opcorpora.xml.bz2'
OPENCORPORA_DNAME = 'opencorpora'
def download_opencorpora(root_dir=None, overwrite=True,
                         noamb=False, nounkn=False):
    """Download the corpus OpenCorpora.
    
    :param root_dir: path to the root storage. If None, default value will
                     be used
    :type root_dir: str
    :param overwrite: False means do not download the corpus if it's already
                      kept in the corpus storage
    :param noamb: download a verstion of the corpus with removed ambiguity
    :param nounkn: download a verstion of the corpus without UNKN tags
                   (used only if *noamb* is True)
    """
    if not noamb:
        nounkn = False
    url = OPENCORPORA_NOAMB_NOUNKN_URL if nounkn else \
          OPENCORPORA_NOAMB_URL if noamb else \
          OPENCORPORA_URL
    return (
        download_corpus(OPENCORPORA + ' 1 of 2', url,
                        dname=OPENCORPORA_DNAME, root_dir=root_dir,
                        overwrite=overwrite, file_noless=1300000 if noamb else
                                                         32000000),
        download_corpus(OPENCORPORA + ' 2 of 2', OPENCORPORA_DICT_URL,
                        dname=OPENCORPORA_DNAME, root_dir=root_dir,
                        overwrite=overwrite, file_noless=16000000)
    )

def remove_opencorpora(root_dir=None):
    """Remove the corpus OpenCorpora.

    :param root_dir: path to the root storage. If None, default value will
                     be used
    :type root_dir: str
    """
    remove_corpus(OPENCORPORA_DNAME, root_dir=root_dir)

RNC = 'RNC'
RNC_URL = 'https://github.com/dialogue-evaluation/morphoRuEval-2017/raw/master/RNC_texts.rar'
RNC_DNAME = 'rnc'
def download_rnc(root_dir=None, overwrite=True):
    """Download the corpus RNC.
    
    :param root_dir: path to the root storage. If None, default value will
                     be used
    :type root_dir: str
    :param overwrite: False means do not download the corpus if it's already
                      kept in the corpus storage
    """
    return download_corpus(RNC, RNC_URL, dname=RNC_DNAME, root_dir=root_dir,
                           overwrite=overwrite, file_noless=5000000)

def remove_rnc(root_dir=None):
    """Remove the corpus RNC.

    :param root_dir: path to the root storage. If None, default value will
                     be used
    :type root_dir: str
    """
    remove_corpus(RNC_DNAME, root_dir=root_dir)

SYNTAGRUS = 'SynTagRus'
SYNTAGRUS_TRAIN_URL = 'https://github.com/UniversalDependencies/UD_Russian-SynTagRus/raw/master/ru_syntagrus-ud-train.conllu'
SYNTAGRUS_DEV_URL = 'https://github.com/UniversalDependencies/UD_Russian-SynTagRus/raw/master/ru_syntagrus-ud-dev.conllu'
SYNTAGRUS_TEST_URL = 'https://github.com/UniversalDependencies/UD_Russian-SynTagRus/raw/master/ru_syntagrus-ud-test.conllu'
SYNTAGRUS_DNAME = 'syntagrus'
def download_syntagrus(root_dir=None, overwrite=True):
    """Download the corpus SynTagRus.
    
    :param root_dir: path to the root storage. If None, default value will
                     be used
    :type root_dir: str
    :param overwrite: False means do not download the corpus if it's already
                      kept in the corpus storage
    """
    fpaths = []
    fpaths.append(download_corpus(SYNTAGRUS + ' 1 of 3', SYNTAGRUS_TRAIN_URL,
                                  dname=SYNTAGRUS_DNAME, root_dir=root_dir,
                                  overwrite=overwrite, file_noless=80000000))
    fpaths.append(download_corpus(SYNTAGRUS + ' 2 of 3', SYNTAGRUS_DEV_URL,
                                  dname=SYNTAGRUS_DNAME, root_dir=root_dir,
                                  overwrite=overwrite, file_noless=10000000))
    fpaths.append(download_corpus(SYNTAGRUS + ' 3 of 3', SYNTAGRUS_TEST_URL,
                                  dname=SYNTAGRUS_DNAME, root_dir=root_dir,
                                  overwrite=overwrite, file_noless=10000000))
    return fpaths

def remove_syntagrus(root_dir=None):
    """Remove the corpus SynTagRus.

    :param root_dir: path to the root storage. If None, default value will
                     be used
    :type root_dir: str
    """
    remove_corpus(SYNTAGRUS_DNAME, root_dir=root_dir)


class _AbstractCorpus:
    """Wrapper for a known corpus, to simplify its usage"""

    name = 'AbstractCorpus'
    _dl_params = ''

    @classmethod
    def train(cls):
        raise ValueError('ERROR: {} does not have a train part'
                             .format(cls.name))

    @classmethod
    def dev(cls):
        raise ValueError('ERROR: {} does not have a dev part'
                             .format(cls.name))

    @classmethod
    def test(cls):
        raise ValueError('ERROR: {} does not have a test part'
                             .format(cls.name))

    @classmethod
    def isfile(cls, fpath):
        if not os.path.isfile(fpath):
            raise FileNotFoundError(
                '{} is not found. Download it first with {}({})'
                    .format(cls.name, cls._dl_name, cls._dl_params)
            )


class AdjustedForSpeech(_AbstractCorpus):
    """Wrapper for a known corpus, adjusted for speech"""

    def __init__(self, cls):
        """
        :param cls: one of the children of _AbstractCorpus
        """
        assert issubclass(cls, _AbstractCorpus), 'ERROR: Unknown input corpus'
        self.name = cls.name
        self.train = lambda: Conllu.fix(cls.train(), adjust_for_speech=True)
        self.dev   = lambda: Conllu.fix(  cls.dev(), adjust_for_speech=True)
        self.test  = lambda: Conllu.fix( cls.test(), adjust_for_speech=True)


class gicr(_AbstractCorpus):
    """Wrapper for GICR corpus"""

    name = GICR
    _dl_name = 'download_gicr'

    @staticmethod
    def _fix(line):
        line = line.strip()
        if line:
            line = line.split('\t')
            if len(line) == 5:
                line = '{}\t{}\t{}\t{}\t_\t{}\t_\t_\t_\t_' \
                           .format(*[x for x in line])
            else:
                raise ValueError('Invalid format')
        return line

    @classmethod
    def train(cls):
        """Return train part of GICR corpus in CONLL-U format"""
        fpath = get_corpus_fpath(dname=GICR_DNAME, url=GICR_URL)
        cls.isfile(fpath)
        return Conllu.load(read_zip(fpath, 'gikrya_new_train.out',
                                    process_line=cls._fix),
                           log_file=LOG_FILE)

    @classmethod
    def test(cls):
        """Return test part of GICR corpus in CONLL-U format"""
        fpath = get_corpus_fpath(dname=GICR_DNAME, url=GICR_URL)
        cls.isfile(fpath)
        return Conllu.load(read_zip(fpath, 'gikrya_new_test.out',
                                    process_line=cls._fix),
                           log_file=LOG_FILE)


re_gdesc     = re.compile('<grammeme parent="(.*)">'
                         '<name>(.+)</name>.+?'
                         '</grammeme>')
re_text      = re.compile('<text id="([^"]+)" parent="([^"]+)" name="([^"]+)">')
re_tag       = re.compile('<tag>(.+)</tag>')
re_paragraph = re.compile('<paragrapg id="(.+)">')
re_sentence  = re.compile('<sentence id="(.+)">')
re_source    = re.compile('<source>(.+)</source>')
re_token     = re.compile('<token id="[^"]+" text="[^"]+">'
                          '<tfr rev_id="[^"]+" t="([^"]+)">(<v>.+</v>)</tfr>'
                          '</token>')
re_v         = re.compile('<v>(<l .+?></l>)</v>')
re_lemma     = re.compile('<l id="[^"]+" t="([^"]+)">(<g .+?/>)?</l>')
re_grammeme  = re.compile('<g v="([^"]+)"/>')
class opencorpora(_AbstractCorpus):
    """Wrapper for OpenCorpora corpus"""

    name = OPENCORPORA
    _dl_name = 'download_opencorpora'

    @classmethod
    def _fix(cls, line):
        line = line.strip()
        rex = re_token.search(line)
        if rex:
           wform, vv = rex.groups()
           res = []
           for v in re_v.findall(vv):
               lemma, grammemes = re_lemma.search(v).groups()
               feats = OrderedDict()
               pos = '_'
               for g in re_grammeme.findall(grammemes):
                   if g == 'gen1':
                       g = 'gent'
                   if g == 'loc1':
                       g = 'loct'
                   feat = cls._gparents.get(g)
                   if feat == 'POST' or feat is None:
                       pos = g
                   else:
                       feats[feat] = g # may override
               res.append('1\t{}\t{}\t{}\t_\t{}\t_\t_\t_\t_\t'
                              .format(wform, lemma, pos,
                                      '|'.join('='.join((x, feats[x]))
                                                   for x in feats)
                                                       if feats else
                                      '_'))
               break  # in the case of ambuguation we add only 1st version
        else:
            rex = re_text.search(line)
            if rex:
                id_, parent, name = rex.groups()
                res = ['# newdoc id = ' + id_,
                       '# parent_doc_id = ' + parent,
                       '# doc_name = ' + unescape(name)]
            else:
                rex = re_tag.search(line)
                if rex:
                    tag, = rex.groups()
                    res = '# tag_{} = {}'.format(cls._tag_id, unescape(tag))
                    cls._tag_id += 1
                else:
                    rex = re_paragraph.search(line)
                    if rex:
                        id_, = rex.groups()
                        res = '# newpar id = ' + id_
                    else:
                        rex = re_sentence.search(line)
                        if rex:
                            id_, = rex.groups()
                            res = '# sent_id = ' + id_
                        else:
                            rex = re_source.search(line)
                            if rex:
                                source, = rex.groups()
                                res = '# text = ' + unescape(source)
                            elif line in [
                                '</sentence>', '</paragraph>', '</text>'
                            ]:
                                res = ''
                                cls._tag_id = 1
                            else:
                                res = None
        return res

    @classmethod
    def train(cls, noamb=False, nounkn=False):
        """Return OpenCorpora corpus in CONLL-U format.

        :param noamb: download a version of the corpus with removed ambiguity
        :param nounkn: download a version of the corpus without UNKN tags
                       (used only if *noamb* is True)
        """
        if not noamb:
            nounkn = False
        url = OPENCORPORA_NOAMB_NOUNKN_URL if nounkn else \
              OPENCORPORA_NOAMB_URL if noamb else \
              OPENCORPORA_URL
        cls._dl_params =   'noamb=True'  if noamb  else '' \
                       + ', nounkn=True' if nounkn else ''
        gparents = {}
        fpath = get_corpus_fpath(dname=OPENCORPORA_DNAME,
                                 url=OPENCORPORA_DICT_URL)
        for line in read_bz2(fpath):
            line = line.strip()
            if line == '</grammemes>':
                break
            else:
                res = re_gdesc.search(line)
                if res:
                    parent, name = res.groups()
                    gparents[name] = parent if parent else name
        for name, p in gparents.items():
            while True:
                parent = p
                p = gparents.get(p)
                if p == parent:
                    break
            gparents[name] = parent
        cls._gparents = gparents

        fpath = get_corpus_fpath(dname=OPENCORPORA_DNAME, url=url)
        cls.isfile(fpath)
        cls._tag_id = 1
        return Conllu.load(
            (x for x in read_bz2(fpath, process_line=cls._fix)
                 if x is not None),
            log_file=LOG_FILE
        )


class rnc(_AbstractCorpus):
    """Wrapper for RNC corpus"""

    name = RNC
    _dl_name = 'download_rnc'

    @staticmethod
    def _fix(line):
        line = line.strip()
        if line:
            line = line.split('\t')
            if len(line) == 5:
                if line[4] != '_':
                    if line[3] == '_':
                        line[3] = line[4]
                    else:
                        line[3] += '|' + line[4]
                line = '1\t{}\t{}\t{}\t_\t{}\t_\t_\t_\t_' \
                           .format(line[0], line[1], line[2], line[3])
            elif (len(line) == 1 and line[0][0] == '=') \
              or (len(line) == 3 and line[0] == 'PUNCT'):
                line = None
            else:
                raise ValueError('Invalid format', line)
        return line

    @classmethod
    def train(cls):
        """Return RNC corpus in CONLL-U format"""
        fpath = get_corpus_fpath(dname=RNC_DNAME, url=RNC_URL)
        cls.isfile(fpath)
        return Conllu.load(
            (x for x in read_rar(fpath,  'RNCgoldInUD_Morpho.conll',
                                 process_line=cls._fix) if x is not None),
            log_file=LOG_FILE
        )


class syntagrus(_AbstractCorpus):
    """Wrapper for SynTagRus corpus"""

    name = SYNTAGRUS
    _dl_name = 'download_syntagrus'

    @classmethod
    def train(cls):
        fpath = get_corpus_fpath(dname=SYNTAGRUS_DNAME,
                                 url=SYNTAGRUS_TRAIN_URL)
        cls.isfile(fpath)
        return Conllu.load(fpath, log_file=LOG_FILE)

    @classmethod
    def dev(cls):
        fpath = get_corpus_fpath(dname=SYNTAGRUS_DNAME,
                                 url=SYNTAGRUS_DEV_URL)
        cls.isfile(fpath)
        return Conllu.load(fpath, log_file=LOG_FILE)

    @classmethod
    def test(cls):
        fpath = get_corpus_fpath(dname=SYNTAGRUS_DNAME,
                                 url=SYNTAGRUS_TEST_URL)
        cls.isfile(fpath)
        return Conllu.load(fpath, log_file=LOG_FILE)


class UniversalDependencies(_AbstractCorpus):
    """Wrapper for SynTagRus corpus"""

    def __init__(self, corpus_name, root_dir=None):
        self.name = '{}/{}'.format(UD, corpus_name)
        self._dl_name = 'download_ud({})'.format(corpus_name)
        self._root_dir = root_dir
        self._corpus_name = corpus_name

    def isfile(self, fpath):
        if not os.path.isfile(fpath):
            raise FileNotFoundError(
                '{} is not found. Download it first with {}()'
                    .format(cls.name, cls._dl_name)
            )

    def train(self):
        fpath = get_ud_train_path(self._corpus_name, root_dir=self._root_dir)
        self.isfile(fpath)
        return Conllu.load(fpath, log_file=LOG_FILE)

    def dev(self):
        fpath = get_ud_dev_path(self._corpus_name, root_dir=self._root_dir)
        self.isfile(fpath)
        return Conllu.load(fpath, log_file=LOG_FILE)

    def test(self):
        fpath = get_ud_test_path(self._corpus_name, root_dir=self._root_dir)
        self.isfile(fpath)
        return Conllu.load(fpath, log_file=LOG_FILE)
