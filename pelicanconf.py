#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import os

AUTHOR = u'Joel Grus'
SITENAME = u'Joel Grus'
SITESUBTITLE = u'is sort of a famous author'
if os.environ.get('LOCALHOST'):
    SITEURL = 'http://localhost:8888'
else:
    SITEURL = os.environ.get('SITEURL', 'https://joelgrus.com')
print("using site url", SITEURL)

THEME = 'themes/pelican-svbhack-joel'
TAGLINE = SITESUBTITLE
USER_LOGO_URL = '/images/joel_headshot.jpeg'

STATIC_PATHS = ['images', 'wp-content', 'experiments', 'static']
READERS = {"html": None}


ARTICLE_URL = '{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = ARTICLE_URL + 'index.html'

PAGE_URL = '{slug}/'
PAGE_SAVE_AS = PAGE_URL + 'index.html'

PATH = 'content'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = u'en'
DEFAULT_CATEGORY = 'old posts'
DISPLAY_CATEGORIES_ON_MENU = False
DEFAULT_PAGINATION = 10
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

DISQUS_SITENAME = 'joelgrus'

MENUITEMS = []#(('Blog', '/'),)

# Feed generation is usually not desired when developing
FEED_DOMAIN = SITEURL
FEED_ALL_ATOM = 'feeds/atom.xml'
FEED_ALL_RSS = 'feeds/rss.xml'
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = []#(('Pelican', 'http://getpelican.com/'),
         #('Python.org', 'http://python.org/'),
         #('Jinja2', 'http://jinja.pocoo.org/'),
         #('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('fa fa-twitter', 'https://twitter.com/joelgrus'),
          ('fa fa-github', 'https://github.com/joelgrus'),
          ('fa fa-linkedin', 'http://www.linkedin.com/in/joelgrus/'))

TWITTER_USERNAME = 'joelgrus'

DEFAULT_PAGINATION = False

# Custom homepage template
INDEX_SAVE_AS = 'blog/index.html'
DIRECT_TEMPLATES = ['index', 'tags', 'categories', 'archives']
PAGINATED_TEMPLATES = {
    'index': None,
    'tag': None,
    'category': None,
    'author': None,
}

# Custom page for homepage
DISPLAY_PAGES_ON_MENU = True

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

MARKDOWN = {
    'extensions': ['codehilite', 'extra'],
    'extension_configs': {
        'codehilite': {
            'guess_lang': False,  # disables automatic highlighting
            'noclasses': True     # optional: inlines styles instead of using CSS classes
        }
    }
}
