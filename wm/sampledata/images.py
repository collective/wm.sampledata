# -*- coding: utf-8 -*-
from functools import wraps
from wm.sampledata import logger
from PIL import Image
from io import BytesIO


import os
import random
import time
import urllib
import requests



# see
# http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
# http://stackoverflow.com/questions/9446387/how-to-retry-urllib2-request-when-failed
def _retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck, e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print msg
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


@_retry(requests.RequestException, tries=5, delay=2, logger=logger)
def _download(url):
    """try to download the url 5 times, with exponential delay.
    first delay 2 seconds, second 4, third 8, etc
    """
    logger.info('Downloading %s' % url)
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0'}  # noqa
    return requests.get(url, headers=headers).content


# Lorempixel.com categories.
CATEGORIES = [
    'abstract', 'animals', 'business',
    'cats', 'city', 'food', 'nightlife',
    'fashion', 'people', 'nature', 'sports',
    'technics', 'transport',
]


def get_placeholder_image(width=1024, height=768,
                          text='',  # default to dimensions of image
                          bkg_color='CCCCCC',
                          text_color='969696'):
    """see https://placeholder.com/ for explanations
    """

    url = u'http://via.placeholder.com/{w}x{h}/{bkg}/{textcolor}'.format(
        w=width,
        h=height,
        bkg=bkg_color.strip('#'),
        textcolor=text_color.strip('#'))

    params = {}
    if text:
        params['text'] = text.encode('utf-8')

    if params:
        url += '?' + urllib.urlencode(params)

    return _download(url)


def test_stub(f):
    """Checks for environment variable "CI=true" and return a  grey jpeg
    generated with pil instead with dimensions width and height
    """

    @wraps(f)
    def f_stub(*args, **kwargs):
        width = 1024
        height = 768
        if len(args) >= 2:
            width, height = args[:2]
        ci = os.environ.get('CI', '0')
        if ci.lower() in ['1', 'true', 'yes', True]:
            logger.info("CI=true set, do not download image")
            img = Image.new("RGB", (width, height), '#bababa')
            with BytesIO() as buffer:
                img.save(buffer, 'JPEG')
                buffer.seek(0)
                return buffer.read()
        return f(*args, **kwargs)

    return f_stub  # true decorator


@test_stub
def getFlickrImage(width=1024, height=768,
                   keywords=[], match_all_keywords=False,
                   gray=False):
    """obtains an image from loremflickr.com.

    If you set match_all_keywords to true it will
    search for all keywords (AND).

    Set gray to True to get a grayscale image.
    """

    url = 'http://loremflickr.com/'
    params = []

    if gray:
        params.append('g')

    params.append('%d/%d' % (width, height))
    params.append(','.join(keywords))
    if match_all_keywords:
        params.append('all')

    url = url + '/'.join(params)

    return _download(url)


@test_stub
def getImage(width=1024, height=768, category=None,
             gray=False, index=None, text=None):
    """obtains an image from lorempixel.com

    for possible categories see ``CATEGORIES``.
    """

    url = 'http://lorempixel.com/'
    params = []

    if gray:
        params.append('g/')
    params.append('%d/%d/' % (width, height))
    if category:
        params.append(category + '/')
        if index:
            params.append('%d/' % index)
    if text:
        params.append('%s/' % text)

    url = url + ''.join(params)

    return _download(url)


RATIOS = [(16, 9), (4, 3)]


def getRandomFlickrImage(long_edge=1024,
                         keywords=[], match_all_keywords=False,
                         gray=None, landscape=None, ratios=RATIOS):
    """Returns a random image from loremflickr.com (portrait or landscape)
    in one of the available RATIOS.

    Set gray to True to force grayscale pictures and to False to force color
    pictures.
    """
    ratio = random.choice(ratios)
    ratio = float(ratio[0]) / ratio[1]

    if landscape is None:
        landscape = random.choice([True, False])

    if gray is None:
        gray = random.choice([True, False])

    if landscape:
        width = long_edge
        height = int(long_edge / ratio)
    else:
        height = long_edge
        width = int(long_edge / ratio)

    return getFlickrImage(
        width, height,
        keywords=keywords,
        match_all_keywords=match_all_keywords,
        gray=gray
    )


def getRandomImage(long_edge=1024, category=None, gray=None,
                   landscape=None, ratios=RATIOS):
    """returns a random image from lorempixel.com (portrait or landscape)
    in one of the available RATIOS

    set gray to True to force grayscale pictures and to False to force color
    pictures
    """
    ratio = random.choice(ratios)
    ratio = float(ratio[0]) / ratio[1]

    if landscape is None:
        landscape = random.choice([True, False])

    if gray is None:
        gray = random.choice([True, False])

    if landscape:
        width = long_edge
        height = int(long_edge / ratio)
    else:
        height = long_edge
        width = int(long_edge / ratio)

    return getImage(width, height, category=category, gray=gray)
