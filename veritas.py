#! /usr/bin/env python3

'''
Andrew Barlow
veritas.py

Description:
Veritas is a program to fetch inspirational quotes a la `fortune` from a list
of authors. Store authors in "author_list.txt". Scrapes quotes from Goodreads.
'''

# LIBRARIES ==================================================

import argparse
import bs4
import os
import random
import re
import requests
import socket

# rich fancy output
from rich.console import Console
from rich.padding import Padding
from rich.progress import track
from rich.text import Text

# GLOBALS ==================================================

base_url = "https://goodreads.com/search?q="

# Var to store authors
authors = []

# use stupid os library to get source file path
script_dir = os.path.dirname(os.path.abspath(__file__))

# filepaths for external files
author_file = f'{script_dir}/author_list.cache'
cache_file = f'{script_dir}/cache.cache'

# INIT ==================================================

# rich modules
console = Console()

# import author list
with open(author_file, "r") as file:

    author_list = file.readlines()
    # strip newlines
    for author in author_list:
        authors.append(author.strip())

# ARGUMENT PARSING ==================================================

parser = argparse.ArgumentParser(
        prog="Veritas",
        description="A font of truth"
    )

parser.add_argument("-c", "--cache", help="get quote from cache", action="store_true")
parser.add_argument("-r", "--random", help="get random quote", action="store_true")
parser.add_argument("-u", "--update", help="update cache", action="store_true")

args = parser.parse_args()

# FUNCTIONS ==================================================

# get_author_quotes_search_url(author) takes a *formatted* author string and
# returns the *url* of a goodreads quote search for that author. It is *not*
# the author's official quote page, and it's verity (hehe) is subject to
# goodreads' search algorithm. this is because goodreads does not have a
# **tab** for authors. To get to an author's page one must pass through an
# intermediate search, or know the author's unique key in advance
def get_author_quotes_search_url(author):
    
    # author_quotes_string contains the API query necessary to specify that the
    # search query is an author, and we want to see quotes
    author_quotes_string = "&search[filed]=author&search[source]=goodreads&search_type=quotes&tab=quotes"


    # contruct query url from base url, the author, and the clarifying API syntax
    url = f"{base_url}{format_author(author)}{author_quotes_string}"

    return url

# search_author_quotes(search_url) executes an http request using a provided
# url formatted for an author and parses+separates quotes from the results
def search_author_quotes(search_url):

    # make http request and store response
    response = requests.get(search_url)

    # raise exception for bad response
    response.raise_for_status()

    # parse response with BeautifulSoup
    parser = bs4.BeautifulSoup(response.text, 'html.parser')

    # only return tag list that are of class quoteText 
    # (which is goodreads' class name for quotes fyi)
    return parser.select('.quoteText')

# request_author_quotes(author) is a high level interface which takes a string
# of the author's name, and returns quotes as a list of strings
def request_author_quotes(author):

    # get formatted url for author
    url = get_author_quotes_search_url(author)

    # request and parse quotes into a list
    quotes = search_author_quotes(url)

    # create empty list to store formatted and filtered quotes
    results = []

    # loop through quotes
    for quote in quotes:

        # when an author can't be verified skip to the next quote
        if verify_author(quote, author) is False:
            # print(quote)
            continue

        # format quote
        formatted_quote = format_quote(quote)

        # add formatted quote to result array
        results.append(formatted_quote)

    return results


# update_cache() fetches all quotes from all sources, and saves them to a txt
# file, separated with line breaks
def update_cache():

    quotes = get_all_quotes()

    with open(cache_file, 'w') as file:

        # pythonic mass exodus of data into the holy standard of a txt file
        # with newline separation
        file.writelines(q + '\n' for q in quotes)

    print(f'Cache saved to {cache_file}')


# HELPER FUNCTIONS ==================================================

# format_author(author) takes a string representation of an author and returns
# a string with the spaces replaced with '+'s. This is for goodreads' API
def format_author(author):
    return author.replace(' ', '+')

# verify_author(quote_tag, author) takes a BS4 quote tag and string of an
# author's name, and returns a bool saying whether that name was found in the
# tag
def verify_author(quote_tag, author):

    # get author field from the scraped quote
    quote_author_field = quote_tag.select_one('.authorOrTitle')

    # move on if empty
    if quote_author_field is None:
        return False

    # check if quote is attributed to author 
    # bc somehow that isn't part of goodreads' algorithm :/
    veri = re.search(author, quote_author_field.getText(), re.IGNORECASE)

    # if no match, skip this quote
    if veri is None:
        return False
    else:
        return True

# get_random_quote() picks a random author, fetches their quotes, and returns a random one
def get_random_quote():
    author = random.choice(authors)
    quotes = request_author_quotes(author)
    return random.choice(quotes)
    
# TODO find way to read random line w/o reading file into memory
def get_quote_from_cache():
    return random.choice(list(open(cache_file))).strip()

# get_all_quotes() fetches and returns all quotes by all authors, may be used
# later for caching/de-networking
def get_all_quotes():
    quotes = []

    # show progress bar for downloading status
    for author in track(authors, description="Downloading quotes"):
        for quote in request_author_quotes(author):
            quotes.append(quote)

    return quotes

# format_quote(quote) is a helper function to remove the formatting errors from
# scraped quotes
def format_quote(quote):
    # extract text
    formatted_quote = quote.getText()
    # strip whitespace
    formatted_quote = formatted_quote.strip()
    # replace multiple spaces in a row with a single space
    formatted_quote = re.sub('\s{2,}', ' ', formatted_quote)

    return formatted_quote

def print_quote(quote_string):

    # separate quote from the author tag
    # goodreads uses one of those weird unicode lookalike hyphens
    quote_array = quote_string.split("—")

    # some quotes have hyphens inside them, we only want it to find the author, so we rejoin the rest
    if len(quote_array) > 2:
        while len(quote_array) > 2:
            quote_array[0] += "-" + quote_array.pop(1)

    rich_quote = Text("")

    rich_quote.append(quote_array[0] + '\n', style="bold")
    rich_quote.append("\n\t- " + quote_array[1], style="italic")

    padding = Padding(rich_quote, 1)
    console.print(padding)

# isConnected() creates a socket and initiates a connection to goodreads to
# test connection
# https://stackoverflow.com/questions/20913412/test-if-an-internet-connection-is-present-in-python
def isConnected():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        sock = socket.create_connection(("www.goodreads.com", 80))
        if sock is not None:
            sock.close
        return True
    except OSError:
        pass
    return False

# checkInternet() is a helper function to mainly avoid dumb mistakes, ala making a
# request w/o a internet connection
def checkInternet():
    if not isConnected():
        print("Error: no connection")
        exit()

# MAIN ==================================================

if __name__ == "__main__":
    if args.cache:
        print_quote(get_quote_from_cache())
    elif args.update:
        checkInternet()
        update_cache()
    elif args.random:
        checkInternet()
        print_quote(get_random_quote())

