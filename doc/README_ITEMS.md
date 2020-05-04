<div align="right"><strong>RuMor: Russian Morphology project</strong></div>
<h2 align="center">Corpuscula: a python NLP library for corpus processing</h2>

`Items` is just a toy database that keeps in memory arrays of entities of
different categories with their attributes. You can construct your own 
objects of that type and save them via `pickle`. `Items` is a useful wrapper 
that is used for keeping the data of named entity domain.

### Usage

The simplest way to create an `Items` database is to just run its constructor
without params:
```python
from corpuscula import Items
items = Items()
```
See below for the parameters of the constructor.

Then, you can load data to `Items`:
```python
items.load(items, items_class=None, update=False, encoding='utf-8-sig',
           log_file=sys.stderr)
```
Param **item** is usually a *dict* ({**item**: {attr: val}}), but it can also
be a *list* or *set* of **item** constants. In the latter case, they will be
transformed to the *dict* of {**item**: {}}.

While loading, orig **item** will be copied to its attributes with a key =
`None`, and if the **item** is of `str` type, then its key in **items** will
be replaced to lowercase version of **items**. It's done for not to keep one
entiny twice in different character cases.

**NB:** It's your responsibility to take care that there are no duplicates 
in the data of **items**. During loading, they will be silently replaced 
by the last one.

**items_class** is a `str` name of the category for your **items** data.
If the category with that name is already present in `Items`, you should
set the **update** parameter to `True`. Elsewise, you'll get an error.

**NB:** `None` is a valid value for the **items_class**.

**log_file** specifies a stream for progress messages. Default is
`sys.stderr`. If **log_file**=`None`, all outputs will be suppressed.

After loading, you can read the data as:
```python
items.get(items_class=None, item=None, copy=True)
```
If **copy** is `True` (default), you'll get a full copy of the data requested.
In that case, changing that data has no effect on the original. But if you
intend to change the data, specify **copy**=`False`. Also, you can use 
**copy**=`False` to speed up your pipeline.

If **item** is `None` (default), you'll get all the **item_class** category as
the return.

**NB**: The `Items` doesn't have methods for changing or removing **item** or
**item_class** keys. So far, we didn't see a necessity in it.

You can check if a certain **item** is present in a certain **item_class**:
```python
items.item_isknown(self, item, item_class)
```

Anytime, you can backup and restore current state of an `Items` object:
```python
o = items.backup()
cdict.restore(o)

items.backup_to(file_path)
items.restore_from(file_path)
```

The constructor of an `Items` class allows to restore and backup data right in 
the moment of an object creation:
```python
items = Items(restore_from=None, backup_to=None)
```
Params **restore_from** and **backup_to** allow to specify file paths for
loading and saving `Items` data. The constructor firstly restores data, and 
only after create a backup of it.

If needed, you can check if current state of an `Items` object does not contain
any information:
```python
if items.isempty():
    [...]
```

### Russian Names Database

As an example `Items` usage, the `data` directory of our github ***Corpuscula*** 
repository contains a csv-file (in Russian) with a list of person's names 
(see `names.zip` file). We couldn't find an open name database anywhere,
so we just crawled the data from open resouces (mostly, it's war heroes and
smth like that, so we have a strong bias to the male side). The repository also 
has the script `scripts/load_names.py` to convert that data to `Items` databases.
The script is complex, but the meaning of it is that we detect a gender of a
person by the patronym. As a result, we got lists of unique names, patronyms
and surnames together with their genders and numbers of occurences. If a name
is unisex, we also keep the number of occurences for every gender.

By default, the script sets thresholds of `5` for names and patronym, and `3`
for surnames. That means that we remove any item that was met less times than 
the specified threshold. We also consider this param when making a conclusion
about name's gender. E.g.: if we met that name as female `2` times and as male
`10` times, then we consider the name as male and just remove its "female part".
The total number of occurences for that case we set to `10`.

We need such pruning because the names we got contain a lot of typos. 
Even setting threshold to `2` decreases names and patronyms thrice (number of
surnames decreases twice). However, maybe, it's worth keeping all the typos, 
because if someone made them once, they are likely to appear again... Anyhow, 
we included the original `names.zip` along with our pruned `Items` files in the
***Corpuscula*** `data` directory. We separate surnames from names and patronyms and
store the data to `surnames.pickle` file. Names and patronyms can be found in
`names.pickle` file.

If you need your own version of names' database, you can change arguments of
the call of the function `load_names_db` at the bottom of the `load_names.py`
script and re-run it. The script saves its result to the directory where you run
it.

**NB:**: Before running the script, unpack the archive `names.zip` in the
`data` directory.
