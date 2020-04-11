<div align="right"><strong>RuMor: Russian Morphology project</strong></div>
<h2 align="center">Corpuscula: a python NLP library for corpus processing</h2>

[![PyPI Version](https://img.shields.io/pypi/v/corpuscula?color=blue)](https://pypi.org/project/corpuscula/)
[![Python Version](https://img.shields.io/pypi/pyversions/corpuscula?color=blue)](https://www.python.org/)
[![License: BSD-3](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/BSD-3-Clause)

A part of ***RuMor*** project. It contains tools to simplify corpus
processing. Highlights are:

* full [*CONLL-U*](https://universaldependencies.org/format.html) support
(includes *CONLL-U Plus*)
* wrappers for known corpora of Russian language
* parser and wrapper for Russian part of *Wikipedia*
* *Corpus Dictionary* that can be used for further morphology processing
* simple database to keep named entities

## Installation

### pip

***Corpuscula*** supports *Python 3.5* or later. To install it via *pip*, run:
```sh
$ pip install corpuscula
```

If you currently have a previous version of ***Corpuscula*** installed, use:
```sh
$ pip install corpuscula -U
```

### From Source

Alternatively, you can also install ***Corpuscula*** from source of this *git
repository*:
```sh
$ git clone https://github.com/fostroll/corpuscula.git
$ cd corpuscula
$ pip install -e .
```
This gives you access to examples and data that are not included to the
*PyPI* package.

## Setup

After installation, you'd like to specify a directory where you prefer to
store downloading corpora:
```python
>>> import corpuscula.corpus_utils as cu
>>> cu.set_root_dir(<path>)  # We will keep corpora here
```
**NB:** it will create/update config file `.rumor` in your home directory.

If you'll not do it, ***Corpuscula*** will try to keep corpora in the
directory where you installed it.

## Usage

[*CONLL-U* Support](https://github.com/fostroll/corpuscula/blob/master/doc/README_CONLLU.md)

[Management of Corpora](https://github.com/fostroll/corpuscula/blob/master/doc/README_CORPORA.md)

[Wrapper for *Wikipedia*](https://github.com/fostroll/corpuscula/blob/master/doc/README_WIKIPEDIA.md)

[*Corpus Dictionary*](https://github.com/fostroll/corpuscula/blob/master/doc/README_CDICT.md)

[Utilities](https://github.com/fostroll/corpuscula/blob/master/doc/README_UTILS.md)

[*Items* database](https://github.com/fostroll/corpuscula/blob/master/doc/README_ITEMS.md)

## License

***Corpuscula*** is released under the BSD License. See the
[LICENSE](https://github.com/fostroll/corpuscula/blob/master/LICENSE) file for more details.
