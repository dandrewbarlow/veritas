# Veritas

by: Andrew Barlow

* [github](https://github.com/dandrewbarlow)
* [website](https://a-barlow.com/dandrewbarlow)

## Description

`Veritas` is a program to fetch and display quotes a la `fortune` from a
customized list of authors. Scrapes quotes from Goodreads, and stores them
locally in a txt file, to be read randomly.

## Usage

```
usage: Veritas [-h] [-c] [-r] [-u]

options:
  -h, --help    show this help message and exit
  -c, --cache   get random quote from cache
  -r, --random  fetch random quote from internet
  -u, --update  fetch all quotes and update cache
```

## Settings

* change settings in global vars
  * e.g. filenames for cache or author list
* default settings are:
  * authors stored in `author_list.txt`
  * cache stored in `cache.txt`
