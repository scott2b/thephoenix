import lxml.html
import sys
import urllib2


def fetch_page(url):
    page = urllib2.urlopen(url).read()
    doc = lxml.html.fromstring(page)
    article = doc.cssselect('div#articlecontent .bodyText')
    print '\n\n'.join([e.text_content() for e in article])


def fetch_author_articles(author):
    url = 'http://thephoenix.com/boston/authors/%s/' % author
    page = urllib2.urlopen(url).read()
    doc = lxml.html.fromstring(page)
    links = doc.cssselect('div#ArticleList h3 a')
    for link in links:
        href = link.get('href')
        if not href.startswith('http:'):
            href = 'http://thephoenix.com%s' % href
        fetch_page(href)


if __name__=="__main__":
    try:
        author = sys.argv[1]
        fetch_author_articles(author) 
    except IndexError:
        print '\nPlease indicate an author\n'
