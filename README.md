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
```bash
pip install stanza
```

If you currently have a previous version of `corpuscula` installed, use:
```bash
pip install stanza -U
```

### From Source

Alternatively, you can also install `corpuscula` from source of this git
repository:
```bash
git clone https://github.com/fostroll/corpuscula.git
cd corpuscula
pip install -e .
```

## Setup

After installation, you'd like to specify a root path where you prefer to store
downloading corpuses:
```python
>>> import corpuscula.corpus_utils as cu
>>> cu.set_root_dir(<path>)  # We will keep corpuses here
```
NB: it will create/update config file .rumor in your home directory.

If you'll not do it, `corpuscula` will try to keep corpuses in the directory
where you installed it.
