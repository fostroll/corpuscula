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

Example (CONLL-U part is from [UD](https://universaldependencies.org/format.html)):
```# sent_id = panc0.s4
# text = तत् यथानुश्रूयते।
# translit = tat yathānuśrūyate.
# text_fr = Voilà ce qui nous est parvenu par la tradition orale.
# text_en = This is what is heard.
1     तत्	तद्	DET     _   Case=Nom|…|PronType=Dem   3   nsubj    _   Translit=tat|LTranslit=tad|Gloss=it
2-3   यथानुश्रूयते	_	_       _   _                         _   _        _   SpaceAfter=No
2     यथा	यथा	ADV     _   PronType=Rel              3   advmod   _   Translit=yathā|LTranslit=yathā|Gloss=how
3     अनुश्रूयते   अनु-श्रु	VERB    _   Mood=Ind|…|Voice=Pass     0   root     _   Translit=anuśrūyate|LTranslit=anu-śru|Gloss=it-is-heard
4     ।      	।	PUNCT   _   _                         3   punct    _   Translit=.|LTranslit=.|Gloss=.
```
