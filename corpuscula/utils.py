# -*- coding: utf-8 -*-
# Corpuscula project: Utilities
#
# Copyright (C) 2019-present by Sergei Ternovykh
# License: BSD, see LICENSE for details
from difflib import SequenceMatcher
import re
import os
import shutil
import sys
from urllib.request import urlopen

LOG_FILE=sys.stderr


def vote(sequence, weights=None):
    """Return a list of unique objects from the *sequence* sorted by frequency.

    :rtype: list[(obj, count, freq)]
    """
    cands = {}
    for o, w in zip(sequence, weights if weights else iter(lambda: 1, 2)):
        cands[o] = cands.get(o, 0) + w
    cnt = sum(cands.values())
    res = [(x, y, y / cnt) for x, y in cands.items()]
    res.sort(key=lambda x: (x[1], x[0]), reverse=True)
    return res

def find_affixes(wform, lemma, lower=False):
    """Find the longest common part of the given *wform* and *lemma*.

    :param lower: if True then return values will be always in lower case
    :return: prefix, common part, suffix/flexion of the *wform*;
             prefix, common part, suffix/flexion of the *lemma*
    :rtype: str, str, str, str, str, str
    """
    if lower:
        lex = wform = wform.lower()
        lem = lemma = lemma.lower()
    else:
        lex = wform.lower()
        lem = lemma.lower()
    lex = lex.replace('ё', 'е')
    lem = lem.replace('ё', 'е')
    a, b, size = SequenceMatcher(None, lex, lem, False) \
        .find_longest_match(0, len(lex), 0, len(lem))
    return wform[:a], wform[a:a + size], wform[a + size:], \
           lemma[:b], lemma[b:b + size], lemma[b + size:]
    #       lemma[:b], wform[a:a + size], lemma[b + size:]

def find_file(prefix, ext=None, dname=None):
    """Return a full name of the file with specified *prefix* if it's present
    in the directory *dname*. If there are several such files, a name of the
    first one will be returned.
    
    :param ext: an extension of the target file
    :param dname: a name of the directory for searching. If None, then the
                  current directory will be used
    """
    for fname in os.listdir(dname):
        if fname.startswith(prefix) and (not ext or fname.endswith('.' + ext)):
            full_fname = os.path.join(dname if dname is not None else '',
                                      fname)
            if os.path.isfile(full_fname):
                res = full_fname
                break
    else:
        res = None
    return res

def rmdir(dname):
    """Remove a directory *dname*"""
    for fname in os.listdir(dname):
        path = os.path.join(dname, fname)
        if os.path.isdir(path):
            rmdir(path)
        else:
            os.remove(path)
    os.rmdir(dname)

def print_progress(current_value, end_value=10, step=1, start_value=0,
                   max_width=60, file=LOG_FILE):
    """Show progress indicator.

    :param end_value: None means unknown; 0 means show finish
    """
    # TODO: optimize all this trash
    cur_value = current_value
    isfinish = False
    if end_value == 0:
        end_value = None
        isfinish = True
    if end_value is not None:
        if start_value:
            cur_value -= start_value
            end_value -= start_value
        end_value /= step
        pend_value = int(end_value) + int(not end_value.is_integer())
    cur_value /= step
    pcur_value = int(cur_value) + int(not cur_value.is_integer())

    full_lines = (pcur_value - 1) // max_width if pcur_value else 0
    if pcur_value > 0:
        pcur_value = pcur_value % max_width
        if pcur_value == 0:
            pcur_value = max_width

    if end_value is not None:
        total_lines = pend_value // max_width + (pend_value % max_width != 0)
        pend_value = min(max_width, pend_value - full_lines * max_width)
        print('\r{}{}{}{}{}{}'.format(
            '>' if full_lines else '[',
            '#' * pcur_value,
            (' ' * (pend_value - pcur_value)),
            ']' if full_lines + 1 >= total_lines else '>',
            ' {:.0f}%'.format(100 * cur_value / end_value),
            ' ' * (max_width - pend_value)
        ), end='' if cur_value < end_value else '\n', file=file)
    else:
        pcur_value += isfinish - 1
        print('\r{}{}{} {}{}'.format(
            '>' if full_lines else '[',
            '=' * pcur_value,
            ']' if isfinish else '>',
            current_value,
            ' ' * (max_width - pcur_value)
        ), end='\n' if isfinish else '', file=file)

COPY_BUF_SIZE = 16 * 1024
CALLBACK_CHUNK_SIZE = 1024 * 1024
def copyfileobj(fsrc, fdst, buf_size=COPY_BUF_SIZE,
                callback=None, callback_chunk_size=CALLBACK_CHUNK_SIZE):
    """Copy data from file-like object *fsrc* to file-like object *fdst*
    (extends shutil.copyfileobj)

    :param fsrc: input stream
    :param fdst: output stream
    :param buf_size: buffer size (in bytes) for r/w operations
    :type buf_size: int
    :param callback: callback function
    :type callback: function(bytes_read, chunks_read, last_chunk_size)
    :param callback_chunk_size: invoke *callback* after every
                                *callback_chunk_size* bytes read
    :type callback_chunk_count: int
    """
    bytes_read = 0
    chunks_read = 0
    chunk_size = 0
    def run_callback_if_need(buf=None):
        nonlocal bytes_read, chunks_read, chunk_size
        urgent_need = False
        if callback:
            if buf:
                buf_len = len(buf)
                bytes_read += buf_len
                chunk_size += buf_len
            elif chunk_size != 0:
                urgent_need = True
            if chunk_size >= callback_chunk_size or urgent_need:
                chunks_read += 1
                callback(bytes_read, chunks_read, chunk_size)
                chunk_size = 0
    while True:
        buf = fsrc.read(buf_size)
        if not buf:
            break
        fdst.write(buf)
        run_callback_if_need(buf)
    run_callback_if_need()

def copy_file(src, dst, buf_size=COPY_BUF_SIZE, **kwargs):
    """Copy data from file *src* to file *dst*.

    :param src: source file name
    :param dst: destination file name
    :param kwargs: params for ``copyfileobj()`` method
    """
    with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
        copyfileobj(fsrc, fdst, **kwargs)

DIR_ACCESS_RIGHTS = 0o755
def download_file(url, dpath=None, fname=None, chunk_size=CALLBACK_CHUNK_SIZE,
                  file_noless=None, overwrite=True, log_msg=None,
                  silent=False):
    """Download file from *url* with progress indicator

    :param url: source url
    :type url: str
    :param dpath: path to the destination directory;
                  if None, then the current work directory will be used
    :type dpath: str
    :param fname: result file name;
                  if None then the name from url will be kept
    :type fname: str
    :param chunk_size: show progress after every *chunk_size* bytes read
    :type chunk_size: int
    :file_noless: if the file is smaller, then don't download it and keep
                  already downloaded one (if exists)
    :type file_noless: int
    :param overwrite: if False and the file is exist, overwrite it
    :type overwrite: bool
    :param log_msg: message that will be printed before downloading
    :type log_msg: str
    :param silent: do not show progress
    :type silent: bool

    :return: path to the downloaded file
    :rtype: str
    """
    if dpath is None:
        dpath = '.'
    if dpath and not os.path.exists(dpath):
        os.makedirs(dpath, DIR_ACCESS_RIGHTS)
    fpath = os.path.join(dpath, re.sub('^.+/', '', url)
                                    if fname is None else fname)
    if overwrite or not os.path.isfile(fpath):
        if not silent and log_msg is not None:
            print(log_msg, file=LOG_FILE)
        fpath_ = fpath + '$'
        with urlopen(url) as f_in:
            f_in_length = f_in.length
            if file_noless is not None:
                if f_in_length is None:
                    raise RuntimeError(
                        'Perhaps the file was removed from the server. '
                        'Check the url manually:\n' + url
                    )
                elif f_in_length < file_noless:
                    raise RuntimeError(
                        'The size of the downloading file less than threshold '
                        '({} bytes vs. {}). '
                            .format(f_in_length, file_noless) +
                        'Check the url manually:\n' + url
                    )
            total_, used_, free_ = shutil.disk_usage(dpath)
            if f_in_length > free_:
                 raise RuntimeError('Not enough space in {} to download file'
                                        .format(dpath))
            chunks_count = f_in_length / CALLBACK_CHUNK_SIZE \
                if f_in_length is not None else None
            if chunks_count is not None:
                chunks_count = int(chunks_count) \
                             + (not chunks_count.is_integer())
            prev_line_no = 0
            if not silent and (chunks_count is None or chunks_count > 2):
                print_progress(0, chunks_count)
            bytes = 0
            try:
                def callback(bytes_read, chunks_read, last_chunk_size):
                    nonlocal bytes
                    bytes = bytes_read
                    prev_line_no = print_progress(
                        bytes_read if chunks_count is None else chunks_read,  # current
                        chunks_count,                                         # end
                        CALLBACK_CHUNK_SIZE if chunks_count is None else 1    # step
                    ) if not silent and (chunks_count is None
                                      or chunks_count > 2) else None
                with open(fpath_, 'wb') as f_out:
                    copyfileobj(
                        f_in, f_out, 
                        callback=callback
                                     if not silent and (chunks_count is None
                                                     or chunks_count > 2) else
                                 None
                    )
            except KeyboardInterrupt as e:
                try:
                    os.remove(fpath_)
                except OSError:
                    pass
                raise e
            if not silent and chunks_count is None:
                print_progress(bytes, 0, CALLBACK_CHUNK_SIZE)
        os.replace(fpath_, fpath)
        if not silent:
            print('done: {} bytes'.format(os.path.getsize(fpath)),
                  file=LOG_FILE)
    return fpath

def read_bz2(apath, encoding='utf-8', errors='ignore', process_line=None):
    """Read lines from a file in bz2 archive.

    :param process_line: a function that will be invoked to process each file's
                         line. If its result is a list, then it will be
                         returned by lines
    :type process_line: callable
    """
    from bz2 import open as bz2_open
    with bz2_open(apath, mode='rt', encoding=encoding, errors=errors) as f:
        for line in f:
            if process_line:
                line = process_line(line)
                if isinstance(line, list):
                    for line_ in line:
                        yield line_
                    continue
            yield line

def read_rar(apath, fname, encoding='utf-8', errors='ignore',
             process_line=None):
    """Read lines from a file in rar archive.

    :param fname: a name of the file in the archive
    :param process_line: a function that will be invoked to process each file's
                         line. If its result is a list, then it will be
                         returned by lines
    :type process_line: callable
    """
    from rarfile import RarFile
    with RarFile(apath) as a:
        with a.open(fname) as f:
            for line in f:
                line = line.decode(encoding=encoding, errors=errors)
                if process_line:
                    line = process_line(line)
                    if isinstance(line, list):
                        for line_ in line:
                            yield line_
                        continue
                yield line

def read_zip(apath, fname, encoding='utf-8', errors='ignore',
             process_line=None):
    """Read lines from a file in zip archive.

    :param fname: a name of the file in the archive
    :param process_line: a function that will be invoked to process each file's
                         line. If its result is a list, then it will be
                         returned by lines
    :type process_line: callable
    """
    from zipfile import ZipFile
    with ZipFile(apath) as a:
        with a.open(fname) as f:
            for line in f:
                line = line.decode(encoding=encoding, errors=errors)
                if process_line:
                    line = process_line(line)
                    if isinstance(line, list):
                        for line_ in line:
                            yield line_
                        continue
                yield line
