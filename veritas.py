#! /usr/bin/env python3

import bs4
import random
import re
import requests

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

def search_author_quotes(search_url):

    # make http request and store response
    response = requests.get(search_url)

    # raise exception for bad response
    response.raise_for_status()

    # parse response with BeautifulSoup
    parser = bs4.BeautifulSoup(response.text, 'html.parser')

    return parser.select('.quoteText')

def request_author_quotes(author):

    url = get_author_quotes_search_url(author)
    quotes = search_author_quotes(url)

    results = []

    for quote in quotes:
        # check if author name is in quote (bc somehow that isn't part of
        # goodreads' algorithm :/ )

        veri = None
        quote_author_field = quote.select_one('.authorOrTitle')


        if quote_author_field is not None:
            veri = re.search(author, quote_author_field.getText(), re.IGNORECASE)
        else:
            continue

        # if no match, skip this quote
        if veri is None:
            continue

        # extract text
        formatted_quote = quote.getText()
        # strip whitespace
        formatted_quote = formatted_quote.strip()
        # replace multiple spaces in a row with a single space
        formatted_quote = re.sub('\s{2,}', ' ', formatted_quote)


        results.append(formatted_quote)

    return results

def format_author(author):
    return author.replace(' ', '+')

def get_random_quote():
    author = random.choice(authors)
    quotes = request_author_quotes(author)
    return random.choice(quotes)
    
def get_all_quotes():
    quotes = []
    for author in authors:
        for quote in request_author_quotes(author):
            quotes.append(quote)

    return quotes

if __name__ == "__main__":
    print(get_random_quote())
