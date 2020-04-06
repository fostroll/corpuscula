<div align="right"><strong>RuMor: Russian Morphology project</strong></div>
<h2 align="center">Corpuscula: a python NLP library for corpus processing</h2>

## Management of Corpora

The package `corpus_utils` contain tools for downloading, store and usage of
known corpora that can be accessed online.

### Setting a root dir where to store downloading corpora

```python
from corpuscula import corpus_utils
corpus_utils.set_root_dir(root_dir)
```
**NB:** it will create/update config file `.rumor` in your home directory.

If you'll not do it, `corpuscula` will try to keep corpora in the directory
where you installed it.

```python
root_dir = corpus_utils.get_root_dir()
```
Receive currently set root dir.

### Manage known corpora

Common attributes for operations below:

**root_dir** in all methods allow to specify alternative root dir location
for any operation. Default is the path from `.rumor` config or, if the config
is not exists, root dir is the root directory of ***Corpuscula*** package.

**overwrite** in downloading methods means force download corpus even it's
already exists. Default is True.

#### [SynTagRus from UniversalDependencies](https://github.com/UniversalDependencies/UD_Russian-SynTagRus/)

```python
corpus_utils.download_syntagrus(root_dir=None, overwrite=True)
corpus_utils.remove_syntagrus(root_dir=None)
```
Download and remove *SynTagRus*.

```python
corpus_utils.syntagrus
corpus_utils.syntagrus.train()
corpus_utils.syntagrus.dev()
corpus_utils.syntagrus.test()
```
Wrappers for the whole *SynTagRus* and its parts.

#### [OpenCorpora](http://opencorpora.org/?page=downloads)

```python
corpus_utils.download_opencorpora(root_dir=None, overwrite=True)
corpus_utils.remove_opencorpora(root_dir=None)
```
Download and remove *OpenCorpora*.

```python
corpus_utils.opencorpora
corpus_utils.opencorpora.train()
```
Wrappers for the whole *OpenCorpora* and its the only part.

#### [GICR from morphoRuEval-2017](https://github.com/dialogue-evaluation/morphoRuEval-2017)

```python
corpus_utils.download_gicr(root_dir=None, overwrite=True)
corpus_utils.remove_gicr(root_dir=None)
```
Download and remove *GICR*.

```python
corpus_utils.gicr
corpus_utils.gicr.train()
corpus_utils.gicr.test()
```
Wrappers for the whole *GICR* and its parts.

#### [RNC from morphoRuEval-2017](https://github.com/dialogue-evaluation/morphoRuEval-2017)

```python
corpus_utils.download_rnc(root_dir=None, overwrite=True)
corpus_utils.remove_rnc(root_dir=None)
```
Download and remove *RNC*.

```python
corpus_utils.rnc
corpus_utils.rnc.train()
```
Wrappers for the whole *RNC* and its the only part.

#### [UD Treebanks](https://github.com/UniversalDependencies)

```python
corpus_utils.download_ud(corpus_name, root_dir=None, overwrite=True)
corpus_utils.remove_rnc(corpus_name, root_dir=None)
```
Download and remove **corpus_name** *UD Treebank*.

```python
corpus = corpus_utils.UniversalDependencies(corpus_name, root_dir=None)
corpus.train()
corpus.dev()
corpus.test()
```
Wrappers for the whole **corpus_name** *UD Treebank* and its parts.

**NB:** The *SynTagRus* wrapper above do exactly the same as the wrapper for
*UD Treebank* with **corpus_name**=UD_Russian_SynTagRus.

### Adjust corpora for speech

Usually, tools for translation speech to text produce output without any care
of punctuation or letters' case of the resulting output. For morphological and
syntactic parsing of such ouput, it is worth to have models trained on corpora
of the same type. ***Corpuscula*** promote a simple way for such
transformation of known corpora:
```python
corpus = corpus_utils.AdjustedForSpeech(corpus_utils.syntagrus)
corpus = corpus_utils.AdjustedForSpeech(UniversalDependencies('UD_Russian_SynTagRus'))
```

Really, any object with `train()`, `dev()`, or `test()` methods can be wrapped
by `corpus_utils.AdjustedForSpeech`. However, if your **corpus** is simply a
[CONLL-U](https://universaldependencies.org/format.html) file or
[Parsed CONLL-U](https://github.com/fostroll/corpuscula/blob/master/doc/TUTORIAL_PARSED_CONLLU.md)
sequence, you can just
use `adjust_for_speech` parameter of `Conllu.load` method:
```python
from corpuscula import Conllu
corpus = Conllu.load(corpus, fix=True, adjust_for_speech=True)
```

Also, if the **corpus** is a *Parsed CONLL-U* sequence, you can invoke `fix`
method of `Conllu` class directly:
```python
from corpuscula import Conllu
corpus = Conllu.fix(corpus, adjust_for_speech=True)
```
Really, the wrapper `corpus_utils.AdjustedForSpeech` do exactly that

### Support for other corpora

The only support for unknown corpora is the possibility to download them to
the common corpora store. If you know the url of any corpora, you can download
it with:
```python
corpus_utils.download_corpus(name, url, dname=None, root_dir=None, fname=None,
                             file_noless=None, overwrite=True, silent=False)
```
Here:

**name**: a name of the downloading corpus.

**url**: url of a downloading file.

**dname**: a name of the directory where to download. The directory will be
created (if not exists) inside your **root_dir**/corpus path.

**fname**: a name of a downloading file. If None then the name from url will
be kept.

**file_noless**: size in bytes. If not None, then check a size of a
downloading file, and if it is smaller, then don't download it and keep
already downloaded one (if exists).

**silent**: suppress progress messages.

To remove corpus, you can invoke:
```python
corpus_utils.remove_corpus(dname, root_dir=None)
```
**dname**: a name of the corpus' directory (located inside **root_dir**/corpus
path).

NB: Param `dname=None` is allowed. In this case *all corpuses will be
deleted*. Be careful. It's a feature.
