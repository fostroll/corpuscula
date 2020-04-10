<div align="right"><strong>RuMor: Russian Morphology project</strong></div>
<h2 align="center">Corpuscula: a python NLP library for corpus processing</h2>

## Wrapper for *Wikipedia*

The package `wikipedia_utils` contain tools to simplify usage *Wikipedia* in NLP
tasks. So far, ***Corpuscula*** supports only Russian part of *Wikipedia*.

### Setting a root directory for store downloaded corpora

```python
from corpuscula import corpus_utils
corpus_utils.set_root_dir(root_dir)
```
**NB:** it will create/update config file `.rumor` in your home directory.

If you won't do it, ***Corpuscula*** will try to keep corpora in the directory
where you installed it.

Next method allows to receive currently set root directory:
```python
root_dir = corpus_utils.get_root_dir()
```

### Downloading and removal Wikipedia dump

```python
from corpuscula import wikipedia_utils
wikipedia_utils.download_(lang='RU', root_dir=None, overwrite=True)
wikipedia_utils.remove_syntagrus(lang='RU', root_dir=None)
```

**lang**: specifies what language you'd like to download *Wikipedia* dump for.
Only **lang**=`'RU'` is supported.

**root_dir**: param allow to specify alternative root directory location.
Default is the path from `.rumor` config or, if the config is not exists, root
directory is the exact directory of ***Corpuscula*** package.

**overwrite**: If `True` (default), force download corpus even if it's already
exists.

### Wrappers for *Wikipedia*'s parts:

```python
from corpuscula import Wikipedia
Wikipedia.titles()
Wikipedia.articles()
Wikipedia.templates()
```
All methods return lists of tuples that are:

for `Wikipedia.titles`: `(<article id>, <article title>)`;

for `Wikipedia.articles`: `(<article id>, <article title>, <article text>)`;

for `Wikipedia.templates`: `(<template id>, <template title>,
<template text>)`;

We promote `Wikipedia.templates` on the case if anyone can make parser for
Wikipedia articles based on that templates. So far, only most common templates
were used for parsing the articles.

**NB:** all methods return just a cleared text, not *CONLL-U*. That's because
for *CONLL-U* we require tokenized text. If you want *Wikipedia* wrapper with
*CONLL-U* tokenized output, refer our
[***Toxic***](https://github.com/fostroll/toxic) library.
