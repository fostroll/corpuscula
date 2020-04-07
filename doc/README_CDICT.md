<div align="right"><strong>RuMor: Russian Morphology project</strong></div>
<h2 align="center">Corpuscula: a python NLP library for corpus processing</h2>

## *Corpus Dictionary*

The class `CorpusDict` parse corpus and gather some statistics that can be
used in further morphology processing pipeline. In particular, the class has
methods to predict *POS*, *LEMMA* and *FEATS* tags of a word form based on
that statistics. Further, that predictions can be used as a hints for more
complicated tagging models. The `CorpusDict` *LEMMA* generator has `0.9809`
accuracy on *SynTagRus* corpus, that is not far from current state of the art.
Adding our [***Morra***](https://github.com/fostroll/morra) library allows to
increase that value upto `0.9873`, and that threshold still stay unbeaten.

### Create, Backup and Restore

The simplest way to create a *Corpus Dictionary* is just invoke its
constructor without params:
```python
from corpuscula import CorpusDict
cdict = CorpusDict()
```
See below for the full parameter list of the constructor.

Then, you can gather statistics from any **corpus** of
[CONLL-U](https://universaldependencies.org/format.html) or
[Parsed CONLL-U](https://github.com/fostroll/corpuscula/blob/master/doc/README_PARSED_CONLLU.md)
format:
```python
cdict.parse(corpus, format='conllu', append=False, log_file=sys.stderr)
```
Param **format** can be `'conllu'` or `'parsed_conllu'`. Default is
`'conllu'`, and it allows to download both of them. The difference is that
when **format**=`'parsed_conllu'`, the **corpus** will be used directly,
without processing via `Conllu.load` method.

If `cdict` already contain data, the try to append it via second invocation of
its `parse` method will throw an error. If you really want to append current
statistics with data of other corpus, specify **append**=`True`.

**log_file** here and in all other methods specifies a stream for progress
messages. Default is `sys.stderr`. If **log_file**=`None`, all output will be
suppressed.

For further usage of the *Corpus Dictionary*, after the **corpus** was
processed, you need to count derived information. It can be done via `fit`
method:
```python
cdict.fit(cnt_thresh=None, ambiguity_thresh=None, log_file=LOG_FILE)
```
Here, **cnt_thresh** (of `int` type) and **ambiguity_thresh** (of `float`) are
parameters that engine is used when it counts a probability that some given
word form has a certain tag. In particular, if any word form has met in the
processed corpus at least **cnt_thresh** times, and it was tagged by the same
label at least in (**ambiguity_thresh** * 100)% cases, then that label will
mark as trusted for that word form.

If params **cnt_thresh** and **ambiguity_thresh** stay unchanged (`None`),
then default values of the constructor of the class will be used (see below).

Anytime, you can backup and restore current state of a `CorpusDict` object:
```python
o = cdict.backup()
cdict.restore(o)

cdict.backup_to(file_path)
cdict.restore_from(file_path)
```

The constructor of a `CorpusDict` class allows all operations above be done
right in the moment of an object creation:
```python
cdict = CorpusDict(restore_from=None, corpus=None, format='conllu',
                   backup_to=None, cnt_thresh=20, ambiguity_thresh=1.,
                   log_file=LOG_FILE):
```
All its parameters were explained above.

If need, you can check if current state of a `CorpusDict` object does not
contain any information:
```python
if cdict.isempty():
    [...]
```

### Usage

#### Getting a summary of processed corpus

All *UPOS* tags:
```python
cdict.get_tags()
```
Return is a set of `str` *UPOS* tag labels in the corpus.

All *UPOS* tags ordered by their frequency:
```python
cdict.get_tags_freq()
```
Return is a list of tuples (<*UPOS* tag> (`str`), <tag count> (`int`), <tag
frequency> (`float`)) ordered by frequency.

All *FEATS* tags:
```python
cdict.get_feats()
```
Return is a dict of all possible keys (`str`) and values (`str`) of *FEATS* in
the corpus.

*UPOS* - *FEATS* matching:
```python
cdict.get_tag_feats(tag)
```
Return is a dict of all possible keys (`str`) and values (`str`) of *FEATS*
for the *UPOS* **tag** given.

