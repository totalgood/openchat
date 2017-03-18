#!python
"""Script and Bot class for interracting with Twitter continuously logging activity to postgresql db

python 2.7 or 3.5

python manage.py shell_plus
>>> run twote/bot python machinelearning ai nlp happy sad depressed angry upset joy bliss unhappy
"""

from __future__ import print_function, unicode_literals, division, absolute_import
from builtins import int, round, str
from future import standard_library
standard_library.install_aliases()
from builtins import object  # NOQA

import os  # NOQA
import time  # NOQA
import random  # NOQA
import sys  # NOQA
import json  # NOQA
from traceback import format_exc  # NOQA
from random import shuffle  # NOQA
import logging  # NOQA

# import peewee as pw  # NOQA
import tweepy  # NOQA

from twote.secrets import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET  # NOQA

loggly = logging.getLogger('loggly')


# 220 unique tags (approximately 20 minutes worth) and 6 repeated tags for pycon2017
DEFAULT_QUERIES = ('#python,#pycon,#portland,#pyconopenspaces,#pycon2017,#pycon2016,' +
                   '#sarcastic,#sarcasm,#happy,#sad,#angry,#mad,#epic,#cool,#notcool,' +
                   '#jobs,#career,#techwomen,' +
                   '#iot,#vr,' +
                   '#angularjs,#reactsjs,#framework,#pinax,#security,#pentest,#bug,#programming,#bot,#robot,' +
                   '#pdxevents,#events,#portlandevents,#techevents,' +
                   '#r,#matlab,#octave,#javascript,#ruby,#rubyonrails,#django,#java,#clojure,#nodejs,#lisp,#golang,' +
                   '#informationtheory,#knowledge,#philosophy,#space,#nasa,' +
                   '#social,#life,#economics,#prosocial,#peaceandcookies,#hugs,#humility,#shoutout,' +
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
                   '"good people","good times","mean people","not good","not bad","pretty good",ok,"not ok",' +
                   'portland,pdx,' +
                   'singularity,"machine intelligence","control problem",future,planet,ecology,"global warming","virtual reality"' +
                   'linguistics,grammar,spelling,language,nlp,natural,tfidf,binomial,multinomial,multivariate,stochastic,' +
                   'semantic,semantics,SVD,PCA,LSI,LDA,SVM,linear,quadratic,"support vector",' +
                   '"infinite series",embedding,polynomial,"hidden layer","visible layer",graph,network,cosine,cos,sine,tangent,' +
                   'einstein,hinton,euler,euclid,bernouli,jung,hobbes,locke,"mark twain",shakespeare,plato,socrates,socratic,' +
                   'sociology,prosocial,antisocial,altruism,"social science","political science",polysci,' +
                   'evolution,genetics,"natural selection",neuroscience,brain,' +
                   'classifier,regression,bayes,' +
                   'pdxpython,pdxruby,pdxdata,quantifiedself,' +
                   '"greater good","total good","common good",totalgood,utilitarianism,generous,commons,friends,family,' +
                   'scikit-learn,scipy,pandas,tensorflow,theano,pythonic,scipy,gensim,sklearn,' +
                   'tired,frustrated,upset,automation,robotics,database,' +
                   'flower,insect,fish,animal,forest,garden,' +
                   'psychology,linguistic,science,astronomy,math,physics,chemistry,biology,medicine,statistics,"computer science",complexity,' +
                   '"deep learning","machine learning","artificial intelligence",' +
                   'quantum,computing,artificial,intelligence,' +
                   'context,clearly,arguably,understanding,learn,abstract,curriculum,studies,study,'
                   'coursera,udacity,udemy,codecademy,codepen,kaggle,khanacademy,"khan academy",' +
                   ':),;),:-),:(,:-(,<3,xoxo,#lol,#rofl,' +
                   'happy,grateful,excited,' +
                   'calagator,' +
                   '"convention center",repl,' +
                   # 6 important tags worth repeating
                   '"portland oregon","portland oregon",' +
                   '"portland or","portland or",' +
                   'pycon,pycon,' +
                   'pycon2017,pycon2017,' +
                   '"pycon 2017","pycon 2017",' +
                   'pyconopenspaces,pyconopenspaces'
                   ).split(',')

try:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(BASE_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openchat.settings")
except:
    print(format_exc())

from twote import models  # NOQA


class Bot(object):

    def __init__(self):
        self.tweet_id_queue = set()
        self.min_queue_len = 1000
        self.max_queue_len = 2000
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(self.auth)
        print('There are {} tweets in the database.'.format(models.Tweet.objects.count()))

    def send_tweet(self, message):
        self.api.update_status(message)
        return message

    def count(self, tags=None):
        tags = ' '.join(tags) if isinstance(tags, (list, tuple)) else tags
        return models.Tweet.objects.count() if tags is None else models.Tweet.objects.filter(tags=' '.join(sorted(tags.split())))

    def search(self, query, quantity=100):
        tweet_list = self.api.search(q=query,
                                     count=quantity,
                                     lang='en')
        print("Retrieved {} candidate tweets.".format(len(tweet_list)))
        return tweet_list

    def _is_acceptable(self, tweet, tag=None, picky=False):
        """
        @brief     This will pull off hash tags just at the end of
                   tweet.  If your tag is not in the ending list
                   the tweet will not be returned
                   Tweets with links are ignored, in case the tag
                   refers to the link and not the text

        @param      self   The object
        @param      tweet  The tweet
        @param      tag    The tag

        @return     the tweet, minus ending tags and the list of tags
                    or False
        """
        if picky and 'http' in tweet.text:
            return False
        else:
            if picky:
                tweet_list = tweet.text.split()
                tag_list = []
                for word in reversed(tweet_list):
                    if word[0] == "#":
                        tag_list.append(word[1:].lower())
                    else:
                        break
            else:
                tag_list = [d['text'].lower() for d in tweet.entities.get('hashtags', [])]
            if tag is not None and tag not in tag_list:
                return False
        return tweet

    def get_tweets(self, ids):
        ids = [str(ids)] if isinstance(ids, (basestring, int)) else list(ids)
        tweets = []
        for i in range(int(len(ids) / 100.) + 1):
            try:
                if i * 100 < len(ids):
                    tweets += list(self.api.statuses_lookup(ids[i * 100:min((i + 1) * 100, len(ids))]))
                # sort-of exponential backoff
                if not i % 2:
                    bot.rate_limit_status = bot.api.rate_limit_status()
                    bot.remaining = bot.rate_limit_status['resources']['application']['/application/rate_limit_status']['remaining']
                    if bot.remaining < 12:
                        time.sleep(8.)
                    if bot.remaining < 6:
                        time.sleep(60.)
                    if bot.remaining < 2:
                        time.sleep(240.)
            except:
                print(format_exc())
        return tweets

    def save_tweet(self, tweet):
        tag_list = [d['text'] for d in tweet.entities.get('hashtags', [])]

        # Find or create the user that tweeted
        user, created = models.User.objects.get_or_create(id_str=str(tweet.user.id))
        user.verified = tweet.user.verified  # v4
        user.time_zone = tweet.user.time_zone  # v4
        user.utc_offset = tweet.user.utc_offset  # -28800 (v4)
        user.protected = tweet.user.protected  # v4
        user.location = tweet.user.location  # Houston, TX  (v4)
        user.lang = tweet.user.lang  # en  (v4)
        user.screen_name = tweet.user.screen_name
        user.followers_count = tweet.user.followers_count
        user.statuses_count = tweet.user.statuses_count
        user.friends_count = tweet.user.friends_count
        user.favourites_count = tweet.user.favourites_count
        user.save()

        # Find or create the tweet this tweet is replying to
        in_reply_to_id_str = tweet.in_reply_to_status_id_str
        if in_reply_to_id_str:
            in_reply_to, created = models.Tweet.objects.get_or_create(id_str=in_reply_to_id_str)
            print("This was reply to: {}".format(in_reply_to_id_str))
            print("Prompt: {}".format(getattr(in_reply_to, 'text', None)))
            print(" Reply: {}".format(getattr(tweet, 'text', None)))
            self.tweet_id_queue = self.tweet_id_queue.union(set([in_reply_to_id_str]))
        else:
            in_reply_to = None

        # Find or create a Place for the location of this tweet
        if tweet.place:
            place, created = models.Place.objects.get_or_create(id_str=tweet.place.id)
            place.url = tweet.place.url
            place.name = tweet.place.name
            place.full_name = tweet.place.full_name
            place.place_type = tweet.place.place_type
            place.country = tweet.place.country
            place.country_code = tweet.place.country_code
            place.bounding_box_coordinates = str(tweet.place.bounding_box.coordinates)
            place.save()
        else:
            place = None

        # Finally we can create the Tweet DB record that depends on all the others
        tweet_record, created = models.Tweet.objects.get_or_create(id_str=tweet.id_str)
        tweet_record.in_reply_to_id_str = in_reply_to_id_str
        tweet_record.in_reply_to = in_reply_to
        tweet_record.id_str = tweet.id_str
        tweet_record.place = place
        tweet_record.user = user
        tweet_record.favorite_count = tweet.favorite_count
        tweet_record.text = tweet.text
        tweet_record.source = tweet.source
        tweet_record.tags = ' '.join(sorted(tag_list))
        tweet_record.save()
        print('SAVED   ' + tweet_record.user.screen_name + ': ' + tweet_record.text)
        return tweet_record

    def clean_tweet(self, tweet):
        """ Strip # character and @usernames out of tweet """
        filter_list = []
        tweet_list = tweet.split()
        for word in tweet_list:
            word = word.replace("#", "")
            if word[0] != '@' and 'http' not in word:
                filter_list.append(word)
        return " ".join(filter_list)

    def process_queue(self, ids=None):
        print('Q' * 100)
        print('Q' * 100)
        self.tweet_id_queue = set(self.tweet_id_queue).union(
            set([str(i) for i in ids]) if isinstance(ids, (list, tuple, set)) else set())
        original_queue = set(self.tweet_id_queue)
        tweets = self.get_tweets(original_queue)
        loggly.info('Trying to save {} prompting tweets.'.format(len(tweets)))
        processed_ids = set([getattr(self.save_tweet(tw), 'id_str', None) for tw in tweets])
        loggly.info('Retrieved {} prompts out of {} ({} unique)'.format(sum([1 for i in processed_ids if i is not None]),
                    len(tweets), len(original_queue)))
        self.tweet_id_queue = original_queue - original_queue.intersection(processed_ids)
        # import ipdb
        # ipdb.set_trace()
        print('Unable to retrieve these {} IDs: {}'.format(len(self.tweet_id_queue), self.tweet_id_queue))
        if len(self.tweet_id_queue) > self.max_queue_len:
            print('There were {} unretrievable tweets (> max_queue_len=={})'.format(
                  len(self.tweet_id_queue), self.max_queue_len))
            self.tweet_id_queue = set(sorted(self.tweet_id_queue)[-self.min_queue_len:])
            print('The newest {} unretrievable tweets were retrained in the queue, the rest deleted, leaving {}.'.format(
                  self.min_queue_len, len(self.tweet_id_queue)))
        return self.tweet_id_queue


# FIXME: use builtin argparse module instead
def parse_args(args):
    min_queries = 20
    num_tweets, delay, picky = None, None, None
    # --picky flag means to ignore any tweets that contain "http" and does not end with one of the desired hashtags
    if '--picky' in args:
        del args[args.index('--picky')]
        picky = True
    hashtags = []
    # the first float found on the command line is the delay in seconds between twitter search queries (default 1 minute)
    # the first int after the first float is the number of tweets to retrieve with each twitter search query
    for arg in args[1:]:
        try:
            num_tweets = int(arg) if not num_tweets else int('unintable')
        except ValueError:
            try:
                delay = float(arg) if delay is None else float('unfloatable')
            except ValueError:
                hashtags += [arg]
    if len(hashtags) < min_queries:
        hashtags += list(DEFAULT_QUERIES)
    delay = 5.0 if delay is None else delay
    num_tweets = num_tweets or 100
    arg_dict = {
        'num_tweets': num_tweets,
        'delay': delay,
        'picky': picky,
        'hashtags': sorted(hashtags),
        }
    print('Parsed args into:')
    print(json.dumps(arg_dict, indent=4))
    return arg_dict


if __name__ == '__main__':
    args = parse_args(sys.argv)
    bot = Bot()
    min_delay = 0.5
    delay_std = args['delay'] * 0.1

    num_before = bot.count()
    while True:
        print('=' * 80)
        # TODO: hashtags attribute of Bot
        #       if more than 15 hashtags just search for them in pairs, tripplets, etc
        hashtags = args['hashtags']
        shuffle(hashtags)
        num_queries = len(hashtags)
        for qid, ht in enumerate(hashtags):
            print('{:03d}/{} Looking for {}'.format(qid, num_queries, ht))
            last_tweets = []
            try:
                for tweet in bot.search(ht, args['num_tweets']):
                    acceptable_tweet = bot._is_acceptable(tweet,
                                                          tag=None if not ht.startswith('#') or not args['picky'] else ht.lstrip('#'),
                                                          picky=args['picky'])
                    if acceptable_tweet:
                        try:
                            last_tweets += [bot.save_tweet(acceptable_tweet)]
                        # print(json.dumps(last_tweets, default=models.Serializer(), indent=2))
                        except TypeError:
                            print('!' * 80)
                            print(format_exc())
                            print()
                            print('Unable to save this tweet: {}'.format(acceptable_tweet))
            except:
                # typical Application Rate Limit Status
                # { "/application/rate_limit_status": {
                #     "reset": 1483911729,
                #     "limit": 180,
                #     "remaining": 179 } }
                print('!' * 120)
                print(format_exc())
                print('!' * 120)
                print(format_exc())
                bot.rate_limit_status = bot.api.rate_limit_status()
                print('Search Rate Limit Status')
                print(json.dumps(bot.rate_limit_status['resources']['search'], default=models.Serializer(), indent=2))
                print('Application Rate Limit Status')
                print(json.dumps(bot.rate_limit_status['resources']['application'], default=models.Serializer(), indent=2))
                print("Unable to retrieve any tweets! Will try again later.")
            print('-' * 120)
            if not (qid % 2):
                bot.rate_limit_status = bot.api.rate_limit_status()
                print('{} ({}) queries allowed within this 15 min window'.format(
                    bot.rate_limit_status['resources']['search']["/search/tweets"]['remaining'],
                    bot.rate_limit_status['resources']['application']['/application/rate_limit_status']['remaining']))
            sleep_seconds = max(random.gauss(args['delay'], delay_std), min_delay)
            print('sleeping for {} s ...'.format(round(sleep_seconds, 2)))
            num_after = bot.count()
            sorted_tweet_id_queue = sorted(bot.tweet_id_queue)
            if len(sorted_tweet_id_queue) > 10:
                print("Missed {} prompts: {}, ... {}".format(
                    len(bot.tweet_id_queue),
                    repr(sorted_tweet_id_queue[:3]).rstrip(']'),
                    repr(sorted_tweet_id_queue[-3:]).lstrip('[')))
            else:
                print("Missed {} prompts: {}".format(
                    len(bot.tweet_id_queue), sorted_tweet_id_queue))

            print("Retrieved {} new tweets with for query {:03d}/{} {} for a total of {} in DB".format(
                num_after - num_before, qid, num_queries, repr(ht), num_after))
            num_before = num_after
            time.sleep(sleep_seconds)
        bot.process_queue()
        time.sleep(30.)

        # bot.tweet(m[:140])
