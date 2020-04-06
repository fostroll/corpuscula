<div align="right"><strong>RuMor: Russian Morphology project</strong></div>
<h2 align="center">Corpuscula: a python NLP library for corpus processing</h2>

## Parsed CONLL-U format

In `corpuscula`, internal representation of *CONLL-U* file is **Parsed
CONLL-U** format. It has a structure as follows. Each sentence stores as a
tuple of two lists: the *tokenized sentence* and the *metadata*. *Tokenized
sentence* is a list of of sentence's tokens, each of those is represented as a
dict with *CONLL-U* fields. All fields' names keeps as constants of `str`
type. Fields' values has an `str` type, too, except *FEATS* and *MISC* fields
that keeps as `OrderedDict` of their components. Keys and values of components
are of `str` type.

*Metadata* stores as `OrderedDict` with `str` keys and values.

Example:
```sh
$ cat example.conllu
# sent_id = 1
# text = Мама мыла раму.
# text_en = Mom washed a chess.
1	Мама	мама	NOUN	_	Animacy=Anim|Case=Nom|Gender=Fem|Number=Sing	_	_	_	Translit=mama|LTranslit=mama|Gloss=mom|
2	мыла	мыть	VERB	_	Aspect=Imp|Gender=Fem|Mood=Ind|Number=Sing|Tense=Past|VerbForm=Fin|Voice=Act	_	_	_	Translit=myla|LTranslit=myt'|Gloss=washed
3	раму	рама	NOUN	_	Animacy=Inan|Case=Acc|Gender=Fem|Number=Sing	_	_	_	SpaceAfter=No|Translit=ramu|LTranslit=rama|Gloss=chess
4	.	.	PUNCT	_	_	_	_	_	Translit=.|LTranslit=.Gloss=.


```

will be converted to:
```python
>>> from pprint import pprint
>>> from corpuscula import Conllu
>>> corpus = Conllu.load('example.conllu', log_file=None)
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
    'MISC': OrderedDict([('Translit', 'mama'),
                         ('LTranslit', 'mama'),
                         ('Gloss', 'mom')]),
    'UPOS': 'NOUN',
    'XPOS': None},
   {'DEPREL': None,
    'DEPS': None,
    'FEATS': OrderedDict([('Aspect', 'Imp'),
                          ('Gender', 'Fem'),
                          ('Mood', 'Ind'),
                          ('Number', 'Sing'),
                          ('Tense', 'Past'),
                          ('VerbForm', 'Fin'),
                          ('Voice', 'Act')]),
    'FORM': 'мыла',
    'HEAD': None,
    'ID': '2',
    'LEMMA': 'мыть',
    'MISC': OrderedDict([('Translit', 'myla'),
                         ('LTranslit', "myt'"),
                         ('Gloss', 'washed')]),
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
                         ('LTranslit', 'rama'),
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
    'MISC': OrderedDict([('Translit', '.'),
                         ('LTranslit', '.'),
                         ('Gloss', '.')]),
    'UPOS': 'PUNCT',
    'XPOS': None}],
  OrderedDict([('sent_id', '1'),
               ('text', 'Мама мыла раму.'),
               ('text_en', 'Mom washed a chess.')]))]
```
