<div align="right"><strong>RuMor: Russian Morphology project</strong></div>
<h2 align="center">Corpuscula: a python NLP library for corpus processing</h2>

## *CoNLL-U* support

The class `Conllu` promotes full *CoNLL-U* format support (including *CoNLL-U
Plus*). The description of *CoNLL-U* format can be found on
[Universal Dependencies](https://universaldependencies.org/format.html)
project site. In ***Corpuscula***, internal representation of *CoNLL-U* file
is in
[*Parsed CoNLL-U*](https://github.com/fostroll/corpuscula/blob/master/doc/README_PARSED_CONLLU.md)
format.

All methods of the class are static. All returning sequences are generators.
Input sequences may be both generators and lists.

### Converting tokenized sentences to *Parsed CoNLL-U*

```python
Conllu.from_sentences(sentences, split_multi=False, adjust_for_speech=False, columns=None)
```
Converts a sequence of tokenized sentences to *Parsed CoNLL-U* format. For every
sentence from **sentences**, the method `Conllu.from_sentence` will be run.
Param **columns** is passed to that method.

Params **split_multi** and **adjust_for_speech** are passed to the method
`Conllu.fix`.

The method returns a sequence of sentences in *Parsed CoNLL-U* format. For
each sentence, *metadata* part contains generated *id* and reconstructed
*text* fields.

```python
Conllu.from_sentence(wforms, columns=None)
```
Converts already tokenized sentence (**wforms** is a list of `str`). Returns
*tokenized sentence* part of *Parsed CoNLL-U* format; *metadata* part won't be
added. All fields of the return will be empty except *ID* and *FORM* fields.
However, if any token contains the symbol `'\u00AD'`, that token will be
splitted, and all parts except the last one will have
`OrderedDict(('SpaceAfter', 'No'))` in the *MISC* field.

By default, the return contains fields of *CoNLL-U* format. If you need any
alternative fields set, you can pass them to the method as a list of `str` via
**columns** param. All non-standard fields will be initialized with `None`.

### Loading *CoNLL-U*

```python
Conllu.load(corpus, encoding='utf-8-sig', fix=True, split_multi=False,
            adjust_for_speech=False, log_file=sys.stderr)
```
**corpus**: a file, a file name or a sequence of text data in *CoNLL-U*
format.

**fix**: need to fix *CoNLL-U* structure while loading.

**split_multi** and **adjust_for_speech**: params to pass to `Conllu.fix`
method. Have no affect if **fix** is `False`.

**log_file**: a stream for progress messages. Default is `sys.stderr`. If
`None`, then output will be suppressed.

Returns sentences in *Parsed CoNLL-U* format

**NB:** For *CoNLL-U Plus* format, the field list must be specified in the first
line of the **corpus** (in the meta variable *global.columns*)

### Save *CoNLL-U*

```python
Conllu.save(corpus, file_path, fix=True, split_multi=False,
            adjust_for_speech=False, log_file=sys.stderr)
```
Saves a **corpus** of *Parsed CoNLL-U* format to *CoNLL-U* file **file_path**.

**fix**: need to fix *CoNLL-U* structure before saving.

**split_multi** and **adjust_for_speech**: params to pass to `Conllu.fix`
method. Have no affect if **fix** is `False`.

**log_file**: a stream for progress messages. Default is `sys.stderr`. If
`None`, then output will be suppressed.

```python
Conllu.get_as_text(corpus, fix=True, split_multi=False,
                   adjust_for_speech=False, log_file=sys.stderr)
```
Converts a **corpus** of *Parsed CoNLL-U* format to text representation of
*CoNLL-U*. All params are equals to the ones of `Conllu.save` method.

Return iterator of `str` lines.

### Fixing *CoNLL-U* structure

```python
Conllu.fix(corpus, split_multi=False, adjust_for_speech=False)
```
If need, restore correct *ID* numeration and adjust sentences' *metadata*.

Params for additional processing:

**split_multi**: if `True`, then wforms with spaces will be processed as
multiword tokens.

**adjust_for_speech**: if `True`, remove all non alphanumeric tokens and
convert all words to lower case. That makes the **corpus** blend in with the
output of speech recognition tools.

Returns sentences in *Parsed CoNLL-U* format

### Merging *CoNLL-U* annotations

Sometimes, we have one corpus tagged independently for different tasks. As
result, we have several copies of the coprus, each with its own annotations.
To merge it in one *CoNLL-U* file, use:
```python
Conllu.merge(corpus1, corpus2, encoding='utf-8-sig', stop_on_error=True,
             log_file=sys.stderr)
```
**corpus1**, **corpus2**: corpora with identical values in the FORM field.
Values in any other fields may be different. Set of fields also don't have to
be equvalent for both corpuses. Result *CoNNL-U* file will include fields from
both of sets.

Param **stop_on_error**: if `True`, the method will raise an error if some
field of any token has non-`None` values in both corpuses and these values are
not equivalent. Note, that non-equivalent values in the FORM field will raise
an error in any case.

**log_file**: a stream for progress messages. Default is `sys.stderr`. If
`None`, then output will be suppressed.

Returns sentences in *Parsed CoNLL-U* format
