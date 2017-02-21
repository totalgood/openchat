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

from traceback import format_exc
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

# 220 unique tags (approximately 20 minutes worth) and 6 repeated tags for pycon2017
DEFAULT_QUERIES = ('#python,#pycon,#portland,#pyconopenspaces,#pycon2017,#pycon2016,#pythonic' +
                   '#sarcastic,#sarcasm,#happy,#sad,#angry,#mad,#epic,#cool,#notcool,' +
                   '#jobs,#career,#techwomen,' +
                   '#angularjs,#reactjs,#framework,#pinax,#security,#pentest,#bug,#programming,#bot,#robot,' +
                   '#calagator,#pdxevents,#events,#portlandevents,#techevents,' +
                   '#r,#matlab,#octave,#javascript,#ruby,#rubyonrails,#django,#java,#clojure,#nodejs,#lisp,#golang,' +
                   '#science,#astronomy,#math,#physics,#chemistry,#biology,#medicine,#statistics,#computerscience,#complexity,' +
                   '#informationtheory,#knowledge,#philosophy,#space,#nasa,' +
                   '#social,#economics,#prosocial,#peaceandcookies,#hugs,#humility,#shoutout,' +
                   '#opendata,#openscience,#openai,#opensource,' +
                   '#data,#dataviz,#d3js,#datascience,#machinelearning,#ai,#neuralnet,#deeplearning,#iot,' +
                   '#hack,#hacking,#hackathon,#compsci,#coding,#coder,#qs,' +
                   '#depressed,#depressing,#gross,#crude,#mean,#tragedy,#lonely,#alone,' +
                   '#mondaymotivation,#motivation,#life,#mind,' +
                   '#play,#game,#logic,#gametheory,#winning,' +
                   '#kind,#bekind,#hope,#nice,#polite,#peace,#inspired,#motivated,#inspiration,#inspiring,#quote,' +
                   '#awesome,#beawesome,#payitforward,#give,#giving,#giveandtake,#love,#pause,#quiet,' +
                   '#windows,#linux,#ubuntu,#osx,#android,#ios,' +
                   '#thankful,#gratitude,#healthy,#yoga,#positivity,#community,#ecosystem,#planet,#meditation,#bliss,' +
                   '@hackoregon,' +
                   '@potus,@peotus,' +
                   '@pycon,@calagator,@portlandevents,@PDX_TechEvents,' +
                   '"good people","good times","mean people","not good","not bad","pretty good",' +
                   'portland,pdx,' +
                   'singularity,"machine intelligence","control problem",future,planet,ecology,"global warming",' +
                   'classifier,regression,bayes,' +
                   'pdxpython,pdxruby,pdxdata,quantifiedself,' +
                   '"greater good","total good","common good",totalgood,utilitarianism,generous,commons,friends,family,' +
                   'scikit-learn,scipy,pandas,tensorflow,pythonic,' +
                   'tired,frustrated,upset,automation,robotics,database,' +
                   'flower,insect,fish,animal,forest,garden,' +
                   'coursera,udacity,udemy,codecademy,codepen,kaggle,khanacademy,"khan academy",' +
                   ':),;),:-),:(,:-(,<3,xoxo,#lol,#rofl,' +
                   'happy,grateful,excited,' +
                   '"convention center",repl,' +
                   # 6 important tags worth repeating
                   '"portland oregon","portland oregon",' +
                   '"portland or","portland or",' +
                   'pycon,pycon,' +
                   'pycon2017,pycon2017,' +
                   '"pycon 2017","pycon 2017",' +
                   'pyconopenspaces,pyconopenspaces'
                   ).split(',')


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
            print_exc()
            return tweets
    if verbose:
        print('Retrieved {} {}tweets for hashtag {}'.format(len(tweets), 'strict ' if strict else '', hashtag))
    return tweets


if __name__ == '__main__':
    tweets = get_tweets()
