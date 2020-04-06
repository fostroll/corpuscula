<div align="right"><strong>RuMor: Russian Morphology project</strong></div>
<h2 align="center">Corpuscula: a python NLP library for corpus processing</h2>

A part of ***RuMor*** project. It contains tools to simplify corpus
processing. Highlights are:

* full CONLL-U support (includes CONLL-U Plus)
* wrappers for known corpora of Russian language
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
downloading corpora:
```python
>>> import corpuscula.corpus_utils as cu
>>> cu.set_root_dir(<path>)  # We will keep corpora here
```
**NB:** it will create/update config file `.rumor` in your home directory.

If you'll not do it, `corpuscula` will try to keep corpora in the directory
where you installed it.

## Usage

[CONLL-U Support](https://github.com/fostroll/corpuscula/blob/master/doc/TUTORIAL_CONLLU.md)

[Wrappers for CORPORA](https://github.com/fostroll/corpuscula/blob/master/doc/TUTORIAL_CORPORA.md)
