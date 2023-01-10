#! /usr/bin/env python3

'''
Andrew Barlow
veritas.py

Description:
Veritas is a program to fetch inspirational quotes a la `fortune`, only from
Christian (or predefined) sources. Scrapes quotes from Goodreads.
'''

# LIBRARIES ==================================================

import bs4
import random
import re
import requests
import socket

# GLOBALS ==================================================

base_url = "https://goodreads.com/search?q="

authors = [
        'Seraphim Rose',
        'G.K. Chesterton',
        'C.S. Lewis',
        'St. Maximus the Confessor',
        'St. Augustine',
        'Pope Benedict XVI',
        'Origen',
        'Gregory of Nyssa',
        'St. John of the Cross',
        'Thomas Merton',
        'Hildegard of Bingen',
        'Meister Eckhart',
        'Catherine of Siena',
        'Isidore of Seville',
        'Thomas Aquinas',
        'Basil the Great'
        ]

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

        # get author field from the scraped quote
        quote_author_field = quote.select_one('.authorOrTitle')

        # move on if empty
        if quote_author_field is None:
            continue

        # check if quote is attributed to author 
        # bc somehow that isn't part of goodreads' algorithm :/
        veri = re.search(author, quote_author_field.getText(), re.IGNORECASE)

        # if no match, skip this quote
        if veri is None:
            continue

        # format quote
        formatted_quote = format_quote(quote)

        # add formatted quote to result array
        results.append(formatted_quote)

    return results

# HELPER FUNCTIONS ==================================================

# format_author(author) takes a string representation of an author and returns
# a string with the spaces replaced with '+'s. This is for goodreads' API
def format_author(author):
    return author.replace(' ', '+')

# get_random_quote() picks a random author, fetches their quotes, and returns a random one
def get_random_quote():
    author = random.choice(authors)
    quotes = request_author_quotes(author)
    return random.choice(quotes)
    
# get_all_quotes() fetches and returns all quotes by all authors, may be used
# later for caching/de-networking
def get_all_quotes():
    quotes = []
    for author in authors:
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

# init() is a helper function to mainly avoid dumb mistakes, ala making a
# request w/o a internet connection
def init():
    if not isConnected():
        print("Error: no connection")
        exit()

# MAIN ==================================================

if __name__ == "__main__":
    init()
    print(get_random_quote())

