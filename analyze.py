#!python
"""Script and Bot class for interracting with Twitter continuously logging activity to postgresql db

python 2.7 or 3.5

python manage.py shell_plus
>>> run twote/bot python machinelearning ai nlp happy sad depressed angry upset joy bliss unhappy
"""

from __future__ import print_function, unicode_literals, division, absolute_import
# from builtins import int, round, str
from future import standard_library
standard_library.install_aliases()
from builtins import object  # NOQA

from traceback import format_exc  # NOQA

import os  # NOQA
import time  # NOQA
import random  # NOQA
import sys  # NOQA
import json  # NOQA
from traceback import format_exc  # NOQA
from random import shuffle  # NOQA
import time  # NOQA

# import peewee as pw  # NOQA
import tweepy  # NOQA

import requests  # NOQA


def get_tweets(url="https://totalgood.org/twote/strict/",
               hashtag='sarcasm', max_count=100,
               strict=True, verbose=True):
    tweets = []
    t0 = t1 = time.time()
    r = requests.get(url, params={'format': 'json', 'hashtag': hashtag})
    while r.status_code == 200 and len(tweets) < max_count:
        t = time.time()
        try:
            js = json.loads(r.text)
            tweets += js['results']
            if verbose:
                print('LAST TWEET {}:\n    {}'.format(
                    tweets[-1]['modified_date'], tweets[-1]['text']))
                print('{}/{} {}/{}'.format(len(tweets), min(max_count, js['count'],
                    t - t1, t - t0)))
            if js['next']:
                r = requests.get(js['next'])
            else:
                break
        except:
            print(format_exc())
            return tweets
    if verbose:
        print('Retrieved {} {}tweets for hashtag {}'.format(len(tweets), 'strict ' if strict else '', hashtag))
    return tweets


if __name__ == '__main__':
    tweets = get_tweets()
