 # -*- coding: utf-8 -*-
"""
Scrape author articles from thephoenix.com

Currenly focused on Boston, although seems to generally be working for the
others. Pass in city before author slug -- defaults to Boston.

There might be a better way: word is that there is a private API.

Usage:
python author_pages.py [city] author-slug

Prints out each article as a JSON structure. Tail author_pages.log to see
script progress.
"""
import datetime
import logging
import json
import sys
import time
import urllib2
import lxml.html

logging.basicConfig(filename='author_pages.log', level=logging.INFO)

SITE_ROOTS = {
    'boston': 'http://thephoenix.com/boston',
    'portland': 'http://portland.thephoenix.com',
    'providence': 'http://providence.thephoenix.com'
}

AUTHOR_URL = '%(site_root)s/authors/%(author_slug)s/'
DELAY=2 # seconds to wait between page fetches


last_fetch = None
def _wait():
    if last_fetch is None:
        return 0
    return DELAY - (datetime.datetime.now() - last_fetch).seconds


def fetch(url):
    global last_fetch
    delta = _wait()
    if delta > 0: 
        logging.info('waiting: %s seconds' % delta)
        time.sleep(delta)
    last_fetch = datetime.datetime.now()
    logging.info('fetching: %s' % url)
    return urllib2.urlopen(url).read()


def prepend_link(city, link):
    assert link.startswith('/'), 'Unsupported relative link'
    if link.lower().startswith('/boston/'):
        link = link[len('/boston'):]
    return '%s%s' % (SITE_ROOTS[city], link)


def next_page_link(links):
    for link in links:
        if 'next' in link.text_content():
            return link


def fetch_author_page(city, url, first=True):
    page = fetch(url)
    doc = lxml.html.fromstring(page)
    title = None
    author = None
    pubdate = None
    if first:
        title = doc.cssselect('div#articlecontent h1')[0].text_content()
        author_span = doc.cssselect('div#articlecontent span.author')[0]
        author = author_span.cssselect('a strong')[0].text_content()
        pubdate = author_span.text_content().split('|')[-1].strip()
    article = doc.cssselect('div#articlecontent .bodyText')
    content = [e.text_content() for e in article]
    next_page = next_page_link(doc.cssselect('div#articlecontent a'))
    if next_page is not None:
        next_pages = fetch_author_page(city, prepend_link(city,
            next_page.get('href')), first=False)
        content += next_pages['content']
    return {
        'title': title,
        'author': author,
        'pubdate': pubdate,
        'content': content
    }
    

def fetch_author_articles(city, author):
    url = AUTHOR_URL % {
        'site_root': SITE_ROOTS[city],
        'author_slug': author
    }
    page = fetch(url)
    doc = lxml.html.fromstring(page)
    links = doc.cssselect('div#ArticleList h3 a')
    for link in links:
        href = link.get('href')
        if not href.startswith('http:'):
            href = prepend_link(city, href)
        print json.dumps(fetch_author_page(city, href))


if __name__=="__main__":
    city = 'boston'
    if len(sys.argv) == 1:
        print '\nPlease indicate an author\n'
        sys.exit(0)
    elif len(sys.argv) == 2:
        city = 'boston'
        author = sys.argv[1]
    else:
        city = sys.argv[1].lower()
        author = sys.argv[2]
    fetch_author_articles(city, author) 
