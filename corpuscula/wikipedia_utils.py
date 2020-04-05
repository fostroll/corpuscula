# -*- coding: utf-8 -*-
# Corpuscula project: Wrapper for Wikipedia
#
# Copyright (C) 2019-present by Sergei Ternovykh
# License: BSD, see LICENSE for details
"""
Tools for downloading and converting Russian part of Wikipedia.
Includes wrapper to simplify the further processing.
"""
from html import unescape
from re import compile as re_compile, match as re_match, sub as re_sub

from .corpus_utils import _AbstractCorpus, \
                          download_corpus, remove_corpus, get_corpus_fpath
from .utils import LOG_FILE, print_progress, read_bz2


WIKIPEDIA_RU = 'Wikipedia.RU'
WIKIPEDIA_RU_URL = 'https://dumps.wikimedia.org/ruwiki/latest/ruwiki-latest-pages-articles.xml.bz2'
WIKIPEDIA_RU_DNAME = 'wikipedia_ru'
def _consts(lang='RU'):
    if lang == 'RU':
        res = {'name' : WIKIPEDIA_RU,
               'url'  : WIKIPEDIA_RU_URL,
               'dname': WIKIPEDIA_RU_DNAME}
    else:
        raise ValueError('ERROR: Lang "{}" is not supported yet'.format(lang))
    return res

def download_wikipedia(lang='RU', root_dir=None, overwrite=True):
    """Downloaded Wikipedia dump.
    
    :param root_dir: path to the root storage. If None, default value will
                     be used
    :type root_dir: str
    :param overwrite: False means do not download the corpus if it's already
                      kept in the corpus storage
    """
    consts = _consts(lang=lang)
    return download_corpus(consts['name'], consts['url'],
                           dname=consts['dname'], root_dir=root_dir,
                           overwrite=overwrite, file_noless=3000000000)

def remove_wikipedia(lang='RU', root_dir=None):
    """Remove Wikipedia dump.

    :param root_dir: path to the root storage. If None, default value will
                     be used
    :type root_dir: str
    """
    remove_corpus(_consts(lang=lang)['dname'], root_dir=root_dir)

def _get_titles(fpath, silent=False):
    return _get_all(fpath, what='titles', silent=silent)

def _get_articles(fpath, silent=False):
    return _get_all(fpath, what='articles', silent=silent)

def _get_templates(fpath, silent=False):
    return _get_all(fpath, what='templates', silent=silent)

re_html = re_compile(r'<[^<>]+?>')
def _get_all(fpath, what=None, silent=False):

    def read_txt():
        with open(fpath, 'rt', encoding='utf-8-sig') as f:
            for line in f:
                yield line

    if not silent:
        print('Process Wikipedia', file=LOG_FILE)
    id_ = title = text = None
    isobject = istable = issquare = 0
    iscomment = False
    inside_tag, tag_cnt = None, 0
    ready_for_save = False
    enters = 0
    istemplate = False
    namespaces = set()

    article_no = -1
    for line_no, line in enumerate(
        read_bz2(fpath) if fpath[-4:].lower() == '.bz2' else read_txt()
    ):

        if text is None:
            line = line.strip()

            ns = re_match(r'<namespace \S+ case="first-letter">'
                          r'([^<]+)</namespace>', line)
            if ns:
                ns, = ns.groups()
                namespaces.add(ns)
                continue

            if line.startswith('<title>'):
                title = re_html.sub('', line)
                pos = title.find(':')
                if pos > 0:
                    ns = title[:pos]
                    if ns in namespaces:
                        if (not what or what == 'templates') and ns == 'Шаблон':
                            istemplate = True
                            title = title[pos + 1:]
                        else:
                            title = None
                            continue
                article_no += 1
                if not silent:
                    print_progress(article_no, end_value=None, step=100000,
                                   file=LOG_FILE)
                id_ = None

            elif not id_ and line.startswith('<id>'):
                id_ = re_html.sub('', line)
                if what == 'titles':
                    yield id_, title

            elif what != 'titles' and title and line.startswith('<text '):
                text = ''

        line_isempty = False
        if text is not None:
            line = line.rstrip()
            if line == '':
                line_isempty = True
            if line.endswith('</text>'):
                ready_for_save = True
            line = re_html.sub('', line)

            if istemplate:
                text += line
                if ready_for_save:
                    yield (id_, title, text) if what else \
                          (id_, title, None, text)
                    id_ = title = text = None
                    istemplate = False
                    ready_for_save = False
                else:
                    text += '\n'
                continue
            if what and what != 'articles':
                continue

            continue_processing = True
            line = unescape(line)
            line_ = None
            while line_ != line:
                if line_ is not None:
                    line = line_
                line_ = re_sub(r'<(\w+)(?:\s[^>]*)?>.*?</\1>', '', line)

            if inside_tag:
                pos = line.rfind('</' + inside_tag + '>')
                if pos >= 0:
                    line = line[pos + 3 + len(inside_tag):]
                    tag_cnt -= 1
                    if not tag_cnt:
                        inside_tag = None
                else:
                    continue_processing = False

            if continue_processing:
                line = re_sub('<[^>]+/>', '', line)
                for token in ('strike', 'math', 'nowiki', 'ref', 'gallery',
                              'imagemap', 'div'):
                    pos = line.find('<' + token)
                    if pos >= 0:
                        line = line[:pos]
                        inside_tag = token
                        tag_cnt += 1
                        break

                line = line.replace('́', '').replace('()', '')
                line = re_html.sub(' ', line)
                if '-->' in line:
                    iscomment = False
                if iscomment:
                    continue
                if '<!--' in line:
                    iscomment = True
                line = re_sub(r'<!--.*', '', line)
                line = re_sub(r'.*-->', '', line)

                for _ in range(1):

                    if line == '----':
                        line = ''
                        break

                    def process_cu(match):
                        head, res_, tail = match.groups()
                        if '[[' in res_ or ']]' in res_:
                            res = ''
                        else:
                            res = re_sub(r'^(?:'
                                r'СС2'
                            r')\|([^|]+)\|([^|]+)\|([^|]+)(?:\|.*)?$',
                            '\g<1> \g<2> \g<3>', res_)
                            if res == res_:
                                res = re_sub(r'^(?:'
                                    r'num|число'
                                r')\|([^|]+)\|([^|]+)(?:\|.*)?$',
                                '\g<1> \g<2>', res_)
                                if res == res_:
                                    res = re_sub(r'^(?:'
                                        r'num|число|lang-\w+|nobr|вьетнамго|'
                                        r'(?:год|year)[^|]*'
                                    r')\|([^|]+)(?:\|.*)?$', '\g<1>', res_)
                                    if res == res_:
                                        res = ''
                        return head + re_sub(r"''+", "", res) + tail

                    line_ = None
                    while line_ != line:
                        if line_ is not None:
                            line = line_
                        line_ = re_sub(r'''(?x)
                            ( (?:^|[^{]) (?:\{\{)* )
                            \{\{
                            (
                                (?:
                                    [{}]? [^{}]
                                )*
                                [{}]?
                            )
                            \}\}
                            ( (?:\}\})* (?:[^}]|$) )
                        ''', process_cu, line)
                    if isobject:
                        cnt = line.count('}}')
                        if cnt > 0:
                            pos = line.rfind('}}')
                            if pos >= 0:
                                line = line[pos + 2:]
                                isobject -= cnt
                    else:
                        line.replace('}}', '')  # just in case

                    line_ = None
                    while line_ != line:
                        if line_ is not None:
                            line = line_
                        line_ = re_sub(r'''(?x)
                            \{\|
                            (
                                (?:
                                    [{}]? [^{}]
                                )*
                                [{}]?
                            )
                            \|\}
                        ''', '', line)
                    if istable:
                        cnt = line.count('|}')
                        if cnt > 0:
                            pos = line.rfind('|}')
                            if pos >= 0:
                                line_ = line[pos + 2:]
                                if not line_ or line_[0] != '}':
                                    line = line_
                                    istable -= cnt
                    else:
                        line.replace('|}', '')  # just in case

                    def process_sq(match):
                        redir, head, res_, tail = match.groups()
                        if redir:
                            res = ''
                        else:
                            res = re_sub(r'(?i)^:?(?:'
                                r'File|Файл|Media|Медиа|Category|Категория'
                            r')\:.+$', '', res_)
                            if res == res_:
                                # [[Москва (город)|Москве]] -> Москве
                                res = re_sub(r'^.+?\|([^|]+?)(?:\|.*)?$', '\g<1>', res_)
                                # [[царство (в биологии)|]] -> царство
                                if res == res_:
                                    res = re_sub(r'^([^|(]+?)\s*\(.+?\)\s*\|\s*',
                                                 '\g<1>', res_)
                                    if res == res_:
                                        # [[Викизнание: Новости|]] -> Новости
                                        res = re_sub(r'^.+?\:([^|:]+)\|\s*',
                                                     '\g<1>', res_)
                                        if res == res_:
                                            # [[sociowiki:Главная Страница]]
                                            # [[:Категория:Газеты Литвы]]
                                            res = re_sub(r'^\:?\S+?\:.+',
                                                         '', res_)
                                            #if res == res_:
                                            #    # [[тест]] -> тест
                                            #    pass
                        return head + re_sub(r"''+", "", res) + tail

                    line_ = None
                    while line_ != line:
                        if line_ is not None:
                            line = line_
                        line_ = re_sub(r'''(?xi)
                            (\#(?:redirect|перенаправление)\s*)?
                            ((?:^|[^\[])(?:\[\[)*)\[\[
                            (
                                (?:
                                    [\[\]]? [^\[\]]
                                )*
                                [\[\]]?
                            )
                            \]\]((?:\]\])*(?:[^\]]|$))
                        ''', process_sq, line)
                    if issquare:
                        cnt = line.count(']]')
                        if cnt > 0:
                            pos = line.rfind(']]')
                            if pos >= 0:
                                line = line[pos + 2:]
                                issquare -= cnt
                    else:
                        line.replace(']]', '')  # just in case

                    isobject_, istable_, issquare_ = isobject, istable, issquare
                    if not (istable or issquare):
                        cnt = line.count('{{')
                        if cnt > 0:
                            pos = line.find('{{')
                            if pos >= 0:
                                line = line[:pos]
                                isobject += cnt
                    if not (isobject or issquare):
                        cnt = line.count('{|')
                        if cnt > 0:
                            pos = line.find('{|')
                            if pos >= 0:
                                line = line[:pos]
                                istable += cnt
                    if not (isobject or istable):
                        cnt = line.count('[[')
                        if cnt > 0:
                            pos = line.find('[[')
                            if pos >= 0:
                                line = line[:pos]
                                issquare += cnt
                    if isobject_ or istable_ or issquare_:
                        continue

                    line_ = line = re_sub(r'^[*#:]+', '', line)
                    line = re_sub(r'^;([^:]*)\:', '\g<1>\n', line)
                    line = re_sub(r'^;([^:]*)', '\g<1>:', line)
                    #line = re_sub(r'^;', '', line)
                    line = re_sub(r'^==+', '', line)
                    line = re_sub(r'\s*==+$', '\n', line)
                    line = re_sub(r'\~~~+', '', line)

                    # [http://freebsd.org Сайт FreeBSD] -> Сайт FreeBSD
                    line = re_sub(r'\[\w+\://\S+\s+([^\[\]]+)\]', ' \g<1> ', line)
                    # [http://freebsd.org/] -> http://freebsd.org/
                    line = re_sub(r'\[(\w+\://[^\s\[\]]+)\]', ' \g<1> ', line)
                    # [mailto:name@example.com name@example.com] -> name@example.com
                    line = re_sub('\[mailto\:[^]]+?([^] ]+)\]', ' \g<1> ', line)
                    line = re_sub(r"''+", "", line)
                    break
                else:
                    continue_processing = False

                if continue_processing:
                    line = unescape(line)
                    line = re_sub(r'[ \t]+', ' ', line)
                    line = line.lstrip()
                    if line != '':
                        enters = line[-1] == '\n'
                    text += line
                    if enters < 2 and not ready_for_save:
                        if line != '' or line_isempty:
                            text += '\n'
                            enters += 1

        if ready_for_save:
            if text and enters:
                text = text[:-enters]
            yield (id_, title, text) if what else \
                  (id_, title, text, None)
            id_ = title = text = None
            isobject = istable = issquare = 0
            iscomment = False
            inside_tag, tag_cnt = None, 0
            ready_for_save = False
            enters = 0

    if article_no >= 0:
        if text:
            yield (id_, title, text) if what else \
                  (id_, title, \
                   None if istemplate else text, \
                   text if istemplate else None)
            article_no += 1
        article_no += 1
        if not silent:
            print_progress(article_no, end_value=0, step=100000, file=LOG_FILE)
            print('Wikipedia has been processed: {} lines, {} articles'
                      .format(line_no + 1, article_no),
                  file=LOG_FILE)


class Wikipedia(_AbstractCorpus):
    """Wrapper for Wikipedia corpus"""

    name = 'Wikipedia'
    _dl_name = 'download_wikipedia'

    def __init__(self, lang='RU', fpath=None, silent=False):
        self.name = _consts(lang=lang)['name']
        self._lang = lang
        if fpath:
            self._fpath = fpath
        self._silent = silent

    def _get_fpath(self):
        consts = _consts(lang=self._lang)
        fpath = self._fpath if hasattr(self, '_fpath') else \
                get_corpus_fpath(dname=consts['dname'], url=consts['url'])
        self.isfile(fpath)
        return fpath

    def titles(self, silent=None):
        return _get_titles(self._get_fpath(),
                           self._silent if silent is None else silent)

    def articles(self, silent=None):
        return _get_articles(self._get_fpath(),
                             self._silent if silent is None else silent)

    def templates(self, silent=None):
        return _get_templates(self._get_fpath(),
                              self._silent if silent is None else silent)
