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
$ pip install stanza
```

If you currently have a previous version of `corpuscula` installed, use:
```sh
$ pip install stanza -U
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
NB: it will create/update config file .rumor in your home directory.

If you'll not do it, `corpuscula` will try to keep corpuses in the directory
where you installed it.

## Usage

### CONLL-U support

The class `Conllu` promotes full CONLL-U format support (including CONLL-U
Plus). The description of CONLL-U format you can find on [Universal
Dependencies](https://universaldependencies.org/format.html) project site.
In `corpuscula`, internal representation of CONLL-U file is Parsed CONLL-U
format. It has a structure as follows.

Each sentence stores as a tuple of two lists: the tokenized sentence and the
metadata. Tokenized sentence is a list of of sentence's tokens, each of those
is represented as a dict with CONLL-U fields. All fields' names keeps as
constants of `str` type. Fields' values has an `str` type, too, except
`FIELDS` and `MISC` fields that keeps as `OrderedDict`s of their components.
Keys and values of components are of `str` type.

Metadata stores as OrderedDict with `str` keys and values.

Example:
```sh
$ cat example.conllu
# sent_id = 1
# text = Мама мыла раму.
# text_en = Mom washed a chess.
1	Мама	мама	NOUN	_	Animacy=Anim|Case=Nom|Gender=Fem|Number=Sing	_	_	_	Translit=mama|Gloss=mom
2	мыла	мыть	VERB	_	Aspect=Imp|Gender=Fem|Mood=Ind|Number=Sing|Tense=Past|VebForm=Fin|Voice=Act	_	_	_	Translit=myla|Gloss=washed
3	раму	рама	NOUN	_	Animacy=Inan|Case=Acc|Gender=Fem|Number=Sing	_	_	_	SpaceAfter=No|Translit=ramu|Gloss=chess
4	.	.	PUNCT	_	_	_	_	_	Translit=.|Gloss=.


```

will be converted to:
```python
>>> from pprint import pprint
>>> from corpuscula import Conllu
>>> corpus = Conllu.load('example.conllu')
>>> pprint(list(corpus))
[([{'DEPREL': None,
    'DEPS': None,
    'FEATS': OrderedDict([('Animacy', 'Anim'),
                          ('Case', 'Nom'),
                          ('Gender', 'Fem'),
                          ('Number', 'Sing')]),
    'FORM': 'Мама',
    'HEAD': None,
    'ID': '1',
    'LEMMA': 'мама',
    'MISC': OrderedDict([('Translit', 'mama'), ('Gloss', 'mom')]),
    'UPOS': 'NOUN',
    'XPOS': None},
   {'DEPREL': None,
    'DEPS': None,
    'FEATS': OrderedDict([('Aspect', 'Imp'),
                          ('Gender', 'Fem'),
                          ('Mood', 'Ind'),
                          ('Number', 'Sing'),
                          ('Tense', 'Past'),
                          ('VebForm', 'Fin'),
                          ('Voice', 'Act')]),
    'FORM': 'мыла',
    'HEAD': None,
    'ID': '2',
    'LEMMA': 'мыть',
    'MISC': OrderedDict([('Translit', 'myla'), ('Gloss', 'washed')]),
    'UPOS': 'VERB',
    'XPOS': None},
   {'DEPREL': None,
    'DEPS': None,
    'FEATS': OrderedDict([('Animacy', 'Inan'),
                          ('Case', 'Acc'),
                          ('Gender', 'Fem'),
                          ('Number', 'Sing')]),
    'FORM': 'раму',
    'HEAD': None,
    'ID': '3',
    'LEMMA': 'рама',
    'MISC': OrderedDict([('SpaceAfter', 'No'),
                         ('Translit', 'ramu'),
                         ('Gloss', 'chess')]),
    'UPOS': 'NOUN',
    'XPOS': None},
   {'DEPREL': None,
    'DEPS': None,
    'FEATS': OrderedDict(),
    'FORM': '.',
    'HEAD': None,
    'ID': '4',
    'LEMMA': '.',
    'MISC': OrderedDict([('Translit', '.'), ('Gloss', '.')]),
    'UPOS': 'PUNCT',
    'XPOS': None}],
  OrderedDict([('sent_id', '1'),
               ('text', 'Мама мыла раму.'),
               ('text_en', 'Mom washed a chess.')]))]
```
