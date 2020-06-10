<div align="right"><strong>RuMor: Russian Morphology project</strong></div>
<h2 align="center">Corpuscula: a python NLP library for corpus processing</h2>

## Management of Corpora

The package `corpus_utils` contains tools for downloading, storing and using
known corpora that can be accessed online.

### Setting a root directory for store downloaded corpora

```python
from corpuscula import corpus_utils
corpus_utils.set_root_dir(root_dir)
```
**NB:** it will create/update config file `.rumor` in your home directory.

If you won't set the root directory, ***Corpuscula*** will try to keep corpora
in the directory where it's installed.

Next method allows to receive currently set root directory:
```python
root_dir = corpus_utils.get_root_dir()
```

### Management of known corpora

Common attributes for operations below:

**root_dir**: in all methods allows to specify alternative root directory
location for any operation. Default is the path from `.rumor` config or, if
the config does not exists, root directory is the exact directory where
***Corpuscula*** is installed.

**overwrite**: if `True` (default), then in downloading methods it means force
download corpus even if it already exists.

#### [*SynTagRus* from UniversalDependencies](https://github.com/UniversalDependencies/UD_Russian-SynTagRus/)

Downloading and removing *SynTagRus*:
```python
corpus_utils.download_syntagrus(root_dir=None, overwrite=True)
corpus_utils.remove_syntagrus(root_dir=None)
```

Wrappers for the whole *SynTagRus* and its parts:
```python
corpus_utils.syntagrus
corpus_utils.syntagrus.train()
corpus_utils.syntagrus.dev()
corpus_utils.syntagrus.test()
```

#### [*OpenCorpora*](http://opencorpora.org/?page=downloads)

Downloading and removing *OpenCorpora*:
```python
corpus_utils.download_opencorpora(root_dir=None, overwrite=True)
corpus_utils.remove_opencorpora(root_dir=None)
```

Wrappers for the whole *OpenCorpora* and its part (only train):
```python
corpus_utils.opencorpora
corpus_utils.opencorpora.train()
```

#### [*GICR* from morphoRuEval-2017](https://github.com/dialogue-evaluation/morphoRuEval-2017)

Downloading and removing *GICR*:
```python
corpus_utils.download_gicr(root_dir=None, overwrite=True)
corpus_utils.remove_gicr(root_dir=None)
```

Wrappers for the whole *GICR* and its parts:
```python
corpus_utils.gicr
corpus_utils.gicr.train()
corpus_utils.gicr.test()
```

#### [*RNC* from morphoRuEval-2017](https://github.com/dialogue-evaluation/morphoRuEval-2017)

Downloading and removing *RNC*:
```python
corpus_utils.download_rnc(root_dir=None, overwrite=True)
corpus_utils.remove_rnc(root_dir=None)
```

Wrappers for the whole *RNC* and its the only part:
```python
corpus_utils.rnc
corpus_utils.rnc.train()
```

#### [*UD Treebanks*](https://github.com/UniversalDependencies)

Downloading and removing **corpus_name** *UD Treebank*:
```python
corpus_utils.download_ud(corpus_name, root_dir=None, overwrite=True)
corpus_utils.remove_ud(corpus_name, root_dir=None)
```

Wrappers for the whole **corpus_name** *UD Treebank* and its parts:
```python
corpus = corpus_utils.UniversalDependencies(corpus_name, root_dir=None)
corpus.train()
corpus.dev()
corpus.test()
```

**NB:** The *SynTagRus* wrapper above behaves exactly the same as the wrapper for
*UD Treebank* with **corpus_name**=`'UD_Russian_SynTagRus'`.

### Adjust corpora for speech

Usually, speech-to-text transcription tools produce texts without considering 
punctuation or letters' case in the resulting output. For morphological and
syntactic parsing of such ouput, it is worth to have models trained on corpora
of the same type. ***Corpuscula*** promotes a simple way for such
transformation of known corpora:
```python
corpus = corpus_utils.AdjustedForSpeech(corpus_utils.syntagrus)
corpus = corpus_utils.AdjustedForSpeech(corpus_utils.UniversalDependencies('UD_Russian_SynTagRus'))
```

Any object with `train()`, `dev()`, or `test()` methods which returns
data in *Parsed CoNLL-U* format can be wrapped by
`corpus_utils.AdjustedForSpeech`. However, if your **corpus** is simply a
[CoNLL-U](https://universaldependencies.org/format.html) file or
[Parsed CoNLL-U](https://github.com/fostroll/corpuscula/blob/master/doc/README_PARSED_CONLLU.md)
sequence, you can just
use `adjust_for_speech` parameter of `Conllu.load` method:
```python
from corpuscula import Conllu
corpus = Conllu.load(corpus, fix=True, adjust_for_speech=True)
```

Also, if the **corpus** is a *Parsed CoNLL-U* sequence, you can run `fix`
method of `Conllu` class directly:
```python
from corpuscula import Conllu
corpus = Conllu.fix(corpus, adjust_for_speech=True)
```
In fact, the wrapper `corpus_utils.AdjustedForSpeech` does exactly that.

### Support for other corpora

The only support for unknown corpora is the possibility to download them to
the common corpora store. If you know the url of any corpora, you can download
it with:
```python
corpus_utils.download_corpus(name, url, dname=None, root_dir=None, fname=None,
                             file_noless=None, overwrite=True, silent=False)
```
Here:

**name**: a name of the corpus to download.

**url**: url of a file to download.

**dname**: a name of the directory where the corpus will be downloaded to. 
The directory will be created (if not exists) inside your **root_dir**/corpus path. 
If **dname** is `None`, param **name** will be used instead.

**fname**: a name of the file to download. If `None`, then the name from url will
be kept.

**file_noless**: size in bytes. If not `None`, then the metod checks a size of
a downloading file, and if it is smaller, then doesn't download it and keeps
already downloaded one (if exists).

**silent**: suppress progress messages.

To remove corpus, you can run:
```python
corpus_utils.remove_corpus(dname, root_dir=None)
```
**dname**: a name of the corpus' directory (located inside **root_dir**/corpus
path).

**NB:** Param **dname**=`None` is allowed. In this case, *all the corpora will
be deleted*. It's a feature. Be careful.
