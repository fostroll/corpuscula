<h2 align="center">Corpuscula: a python NLP library for corpus processing</h2>

A part of RuMor project. It contain tools that simplify corpus processing.
Highlights are:

* full CONLL-U support (includes CONLL-U Plus)
* wrappers for known corpuses of Russian language
* parser and wrapper for russian part of Wikipedia
* corpus dictionary that can be used for further morphology processing
* simple database to keep named entities

## Installation

### pip

Corpuscula supports Python 3.5 or later. To install it via pip, run:
```sh
$ pip install corpuscula
```

If you currently have a previous version of `corpuscula` installed, use:
```sh
$ pip install corpuscula -U
```

### From Source

Alternatively, you can also install `corpuscula` from source of this git
repository:
```sh
S git clone https://github.com/fostroll/corpuscula.git
S cd corpuscula
S pip install -e .
```

## Setup

After installation, you'd like to specify a root path where you prefer to store
downloading corpuses:
```python
>>> import corpuscula.corpus_utils as cu
>>> cu.set_root_dir(<path>)  # We will keep corpuses here
```
NB: it will create/update config file `.rumor` in your home directory.

If you'll not do it, `corpuscula` will try to keep corpuses in the directory
where you installed it.

## Usage

### CONLL-U support

The class `Conllu` promotes full *CONLL-U* format support (including *CONLL-U
Plus*). The description of *CONLL-U* format you can find on [Universal
Dependencies](https://universaldependencies.org/format.html) project site.
In `corpuscula`, internal representation of *CONLL-U* file is [Parsed
CONLL-U](https://github.com/fostroll/corpuscula/blob/master/doc/TUTORIAL_PARSED_CONLLU.md)
format.

All methods of the class are static. All returning sequences are generators.
Input sequences may be generators or lists.

**`Conllu` class methods**

`Conllu.from_sentence(wforms, columns=None)`

Converts already tokenized sentence (**wforms** is a list of `str`). Returns
*tokenized sentence* part of *Parsed CONLL-U* format; *metadata* part won't be
added. All fields of the return will be empty except *ID*, *FORM*. However, if
any token contain the symbol `'\u00AD`, that token will be splitted and all
parts except the last one will have `OrderedDict(('SpaceAfter', 'No'))` in the
*MISC* field.

By default, the return contain fields of *CONLL-U* format. If you need some
alternative fields set, you can pass them to the method as list of `str` via
**columns** param. All non-standard fields will be initialized with `None`.

`Conllu.from_sentences(sentences, split_multi=False, adjust_for_speech=False, columns=None)`

Convert sequence of tokenized sentences to *Parsed CONLL-U* format. For every
sentence from **sentences** the method `Conllu.from_sentence` will be invoked.
Param **columns** is passed to that method.

Params **split_multi** and **adjust_for_speech** are passed to the method
`Conllu.fix`.

Returns a sequence of sentences in *Parsed CONLL-U* format. For each 
sentence, *metadata* part contain a generated *id* and reconstructed *text*
fieds.
