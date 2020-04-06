<div align="right"><strong>RuMor: Russian Morphology project</strong></div>
<h2 align="center">Corpuscula: a python NLP library for corpus processing</h2>

## *CONLL-U* support

The class `Conllu` promotes full *CONLL-U* format support (including *CONLL-U
Plus*). The description of *CONLL-U* format you can find on
[Universal Dependencies](https://universaldependencies.org/format.html)
project site. In ***Corpuscula***, internal representation of *CONLL-U* file
is
[*Parsed CONLL-U*](https://github.com/fostroll/corpuscula/blob/master/doc/README_PARSED_CONLLU.md)
format.

All methods of the class are static. All returning sequences are generators.
Input sequences may be both generators and lists.

### Converting tokenized sentences to *Parsed CONLL-U*

```python
Conllu.from_sentences(sentences, split_multi=False, adjust_for_speech=False, columns=None)
```
Converts sequence of tokenized sentences to *Parsed CONLL-U* format. For every
sentence from **sentences**, the method `Conllu.from_sentence` will be
invoked. Param **columns** is passed to that method.

Params **split_multi** and **adjust_for_speech** are passed to the method
`Conllu.fix`.

The method returns a sequence of sentences in *Parsed CONLL-U* format. For
each sentence, *metadata* part contain a generated *id* and reconstructed
*text* fieds.

```python
Conllu.from_sentence(wforms, columns=None)
```
Converts already tokenized sentence (**wforms** is a list of `str`). Returns
*tokenized sentence* part of *Parsed CONLL-U* format; *metadata* part won't be
added. All fields of the return will be empty except *ID* and *FORM* fields.
However, if any token contain the symbol `'\u00AD'`, that token will be
splitted, and all parts except the last one will have
`OrderedDict(('SpaceAfter', 'No'))` in the *MISC* field.

By default, the return contain fields of *CONLL-U* format. If you need some
alternative fields set, you can pass them to the method as a list of `str` via
**columns** param. All non-standard fields will be initialized with `None`.

### Loading *CONLL-U*

```python
Conllu.load(corpus, encoding='utf-8-sig', fix=True, split_multi=False,
            adjust_for_speech=False, log_file=sys.stderr)
```
**corpus**: a file, a file name or a sequence of text data in *CONLL-U*
format.

**fix**: need to fix a *CONLL-U* structure while loading.

**split_multi** and **adjust_for_speech**: params to pass to `Conllu.fix`
method. Have no affect if **fix** is `False`.

**log_file**: stream for progress messages. Default is `sys.stderr`. If
`None`, then output will be suppressed.

**NB:** For *CONLL-U Plus* format, the field list must be specified in the first
line of the **corpus** (in the meta variable *global.columns*)

### Save *CONLL-U*

```python
Conllu.save(corpus, file_path, fix=True, split_multi=False,
            adjust_for_speech=False, log_file=sys.stderr)
```
Saves a **corpus** of *Parsed CONLL-U* format to *CONLL-U* file **file_path**.

**fix**: need to fix *CONLL-U* structure before save.

**split_multi** and **adjust_for_speech**: params to pass to `Conllu.fix`
method. Have no affect if **fix** is `False`.

**log_file**: stream for progress messages. Default is `sys.stderr`. If
`None`, then output will be suppressed.

```python
Conllu.get_as_text(corpus, fix=True, split_multi=False,
                   adjust_for_speech=False, log_file=sys.stderr)
```
Converts a **corpus** of *Parsed CONLL-U* format to text representation of
*CONLL-U*. All params are equals to the ones of `Conllu.save` method.

### Fixing *CONLL-U* structure

```
Conllu.get_as_text(corpus, split_multi=False, adjust_for_speech=False)
```
If need, restore correct *ID* numeration and adjust sentences' *metadata*.

Params for additional processing:

**split_multi**: if `True`, then wforms with spaces will be processed as
multiword tokens.

**adjust_for_speech**: if `True`, remove all non alphanumeric tokens and
convert all words to lower case. That makes the **corpus** blends in with the
output of speech recognizing tools.
