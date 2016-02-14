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
    SITEURL = 'http://joelgrus.com'

THEME = 'themes/pelican-svbhack-joel'
TAGLINE = SITESUBTITLE
USER_LOGO_URL = '/images/joel.png'

STATIC_PATHS = ['images', 'wp-content', 'experiments']

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
SOCIAL = (('Twitter', 'https://twitter.com/joelgrus'),
          ('Facebook', 'https://www.facebook.com/joel.grus'),
          ('Google+', 'https://plus.google.com/+JoelGrus'),
          ('LinkedIn', 'http://www.linkedin.com/in/joelgrus/'))

TWITTER_USERNAME = 'joelgrus'

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
