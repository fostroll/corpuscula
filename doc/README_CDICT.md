<div align="right"><strong>RuMor: Russian Morphology project</strong></div>
<h2 align="center">Corpuscula: a python NLP library for corpus processing</h2>

## *Corpus Dictionary*

The class `CorpusDict` parse training corpus and gather some statistics that
can be used in further morphology processing pipeline. Also, the class has
methods to predict *POS*, *LEMMA* and *FEATS* tags of a word form based on
that statistics. Further, that predictions can be used as a hints for more
complicated tagging models. The *LEMMA* generator of the `CorpusDict` has
`0.9809` accuracy on *SynTagRus* corpus, that is not far from current state of
the art. Adding our [***Morra***](https://github.com/fostroll/morra) library
allows to increase that value upto `0.9873`, and that threshold still stay
unbeaten.

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
word form has a certain tag. In particular, if any word form was met in the
processed corpus at least **cnt_thresh** times, and it was tagged by the same
label at least in (**ambiguity_thresh** * 100)% cases, then that label will
mark as *trusted* for that word form.

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

### Getting a summary of the corpus processed

Get a most common *UPOS* tag:
```python
cdict.most_common_tag()
```
Returns a most common *UPOS* tag label (`str`) for the training corpus.

All *UPOS* tags:
```python
cdict.get_tags()
```
Returns a set of `str` *UPOS* tag labels in the training corpus.

All *UPOS* tags ordered by their frequency:
```python
cdict.get_tags_freq()
```
Returns a list of tuples (*UPOS* tag (`str`), tag count (`int`), tag frequency
(`float`)) ordered by frequency.

All *FEATS* tags:
```python
cdict.get_feats()
```
Returns a dict of all possible keys (`str`) and values (`str`) of *FEATS* in
the training corpus.

*UPOS* - *FEATS* matching:
```python
cdict.get_tag_feats(tag)
```
Returns a dict of all possible keys (`str`) and values (`str`) of *FEATS*
for the *UPOS* **tag** given.

*FEATS* tags ordered by frequency:
```python
cdict.get_feats_freq(tag)
```
Returns a list of ordered by frequency tuples (*FEATS* key (`str`), key count
(`int`), key frequency (`float`)) of all possible *FEATS* keys for the given
*UPOS* **tag**.

*FEATS* values ordered by frequency:
```python
cdict.get_feat_vals_feats(tag, feat)
```
Returns a list of ordered by frequency tuples (*FEATS* value (`str`), 
value count (`int`), value frequency (`float`)) of all possible *FEATS* values
for the given *UPOS* **tag** and *FEATS* key **feat**.

### Make hint predictions

Predict the *UPOS* tag label:
```python
cdict.predict_tag(wform, isfirst=False, cnt_thresh=None)
```
Returns a tuple of an *UPOS* tag predicted and a relevance coef. If the word
form **wform** has a *trusted* tag label, then returns that tag with a
relevance coef equals to 1. Elsewise, we choose the most common tag for
**wform** and calculate some empirical value as a relevance coef.

Param **isfirst** pointed whether the **wform** is a first word in the
sentence.

**cnt_thresh** detects, when we must put a penalty on the our prediction
because of a lack of data. If the **wform** was met in the training corpus
less than **cnt_thresh** times, then the relevance coef will be discounted by
(count / **cnt_thresh**).

If **cnt_thresh** is not specified (`None`), then the default value of the
constructor of the class will be used.

**NB:** If the **wform** is not known, the method returns (`None`, `None`).

Predict the *LEMMA* field value:
```python
cdict.predict_lemma(wform, tag, isfirst=False, cnt_thresh=None)
```
Returns a tuple of a lemma and a relevance coef. If the word form **wform**
has a *trusted* lemma, then returns it with a relevance coef equals to 1.
Elsewise, we choose the most common lemma for **wform** and *UPOS* **tag**
and calculate some empirical value as a relevance coef.

If the **wform** is not known, we try to construct the lemma based on words
from the training corpus dictionary that have similar endings. We set
relevance coef = `0` for such cases. Also, we just set (lemma = **wform**,
relevance coef = `0`) if **wform** is non-alpha.

Params **isfirst** and **cnt_thresh** has the same meaning as the ones of 
`CorpusDict.predict_tag` method.

Predict the *FEATS* tag value:
```python
cdict.predict_feat(feat, wform, lemma, tag, cnt_thresh=None)
```
Search a tuple of a most common *FEATS* tag value for a certain *FEATS* tag
key **feat** by a given word form **wform**, word's **lemma** and an *UPOS*
**tag**. Returns a tuple of a value found and a relevance coef. If the value
counted as *trusted*, then the relevance coef set to 1. Elsewise, we calculate
for it some empirical value.

If we can't find the value, we return (`None`, `None`).

Param **cnt_thresh** has the same meaning as the one of
`CorpusDict.predict_tag` method.

### Supplements

You can check if a certain word form was met in the training corpus:
```python
cdict.wform_isknown(wform, tag=None)
```
Optional param **tag** allow to specify an *UPOS* tag label for a word form
**wform**.
