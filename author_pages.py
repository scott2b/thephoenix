"""
Scrape author articles from thephoenix.com

Currenly focused on Boston, although seems to generally be working for the
others. Pass in city before author slug -- defaults to Boston.

There might be a better way: word is that there is a private API.

Usage:
python author_pages.py [city] author-slug
"""
import lxml.html
import sys
import urllib2

SITE_ROOTS = {
    'boston': 'http://thephoenix.com/boston',
    'portland': 'http://portland.thephoenix.com',
    'providence': 'http://providence.thephoenix.com'
}

AUTHOR_URL = '%(site_root)s/authors/%(author_slug)s/'

def prepend_link(city, link):
    assert link.startswith('/'), 'Unsupported relative link'
    if link.lower().startswith('/boston/'):
        link = link[len('/boston'):]
    return '%s%s' % (SITE_ROOTS[city], link)

def fetch_page(url):
    page = urllib2.urlopen(url).read()
    doc = lxml.html.fromstring(page)
    article = doc.cssselect('div#articlecontent .bodyText')
    print '\n\n'.join([e.text_content() for e in article])


def fetch_author_articles(city, author):
    url = AUTHOR_URL % {
        'site_root': SITE_ROOTS[city],
        'author_slug': author
    }
    page = urllib2.urlopen(url).read()
    doc = lxml.html.fromstring(page)
    links = doc.cssselect('div#ArticleList h3 a')
    for link in links:
        href = link.get('href')
        if not href.startswith('http:'):
            href = prepend_link(city, href)
        print 'fetching', href
        fetch_page(href)


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
