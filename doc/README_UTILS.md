<div align="right"><strong>RuMor: Russian Morphology project</strong></div>
<h2 align="center">Corpuscula: a python NLP library for corpus processing</h2>

## Utilities

The package contains a bunch of utilities that can sometimes be useful. Here
we show just unsorted list of them.

Sort objects by their frequency:
```python
vote(sequence, weights=None)
```
Parse objects from the **sequence** and return a list of tuples (object,
count, frequency) sorted by frequency.

Param **weights** allows to specify a weight of each element in the
**sequence**. By default, all weights are ones.

Find the longest common part of a word form with its lemma:
```python
find_affixes(wform, lemma, lower=False)
```
Returns a tuple of 6 values: prefix, common part, suffix/flexion of the
**wform**; prefix, common part, suffix/flexion of the **lemma**.

If **lower** is `True` then both **wform** and **lemma** will be converted to
lower case before comparison. Thus, all return values will be in lower case,
too.

**NB:** Russian letters 'е' and 'ё' counts equal while comparison

Find a full file name by its **prefix**:
```python
find_file(prefix, ext=None, dname=None)
```
**ext**: an extension of the target file

**dname**: a name of the directory for searching. If **dname** is `None`
(default), then the current directory will be used.

**NB:** If the directory **dname** contain several such files, only the name
of the first one will be returned.

Recursively remove directory **dname**:
```python
rmdir(dname)
```

Progress indicator:
```python
print_progress(current_value, end_value=10, step=1, start_value=0,
               max_width=60, file=sys.stderr)
```
If **end_value** is not `None` and greater than `0`, then indicator shows a
value in percents. Elsewise, it shows absolute value.

**end_value** == `0` means the end of iterations. Indicator shows final
status.

**max_width** allow to change max width of the indicator in characters.

The meaning of **current_value**, **step** and **start_value** params is
obvious.

Copy file with a **callback** function. For example, you can use it to show
progress indicator:
```python
copyfileobj(fsrc, fdst, buf_size=16 * 1024,
            callback=None, callback_chunk_size=1024 * 1024)
```
**fsrc**, **fdst** - file descriptors of input and output file streams.
**callback**: a function. Its params: *bytes_read*, *chunks_read*,
*last_chunk_size*.
**callback_chunk_size**: invoke **callback** after every
**callback_chunk_size** bytes read.

The same for just a source (**src**) and destination (**dst**) file names:
```python
copy_file(src, dst, buf_size=16 * 1024,
          callback=None, callback_chunk_size=1024 * 1024)
```

Download a file from **url**:
```python
download_file(url, dpath=None, fname=None, chunk_size=1024 * 1024,
              file_noless=None, overwrite=True, log_msg=None,
              silent=False)
```
**dpath**: path to the destination directory. If `None`, then the current work
directory will be used.

**fname**: result file name. If `None`, then the name from **url** will be
kept.

**chunk_size**: show progress after every **chunk_size** bytes read.

**file_noless** if the file is smaller, then don't download it and keep
already downloaded one (if exists).

**overwrite**: if `False` and the file is exist, overwrite it.

**log_msg**: message that will be printed before downloading.

**silent**: do not show progress.

Read lines from a file in *bz2* archive:
```python
read_bz2(apath, encoding='utf-8', errors='ignore', process_line=None)
```
Param **process_line** is a callback function that will be invoked to process
each file's line. If its result is a list, then it will be returned by lines.

Read lines from a file in *rar* archive:
```python
read_rar(apath, fname, encoding='utf-8', errors='ignore', process_line=None)
```
Param **process_line** - as above.

Read lines from a file in *zip* archive:
```python
read_zip(apath, fname, encoding='utf-8', errors='ignore', process_line=None)
```
**name**: a name of the file in the archive.

Param **process_line** - as above.
