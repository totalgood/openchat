import datetime
import django
import logging 
import os
import re

import pytz
from nltk import word_tokenize
from slacker import Slacker
from sutime import SUTime
import tweepy
from tweepy.api import API 

# need to point Django at the right settings to access pieces of app
os.environ["DJANGO_SETTINGS_MODULE"] = "openchat.settings"
django.setup()

from openspaces.bot_utils import db_utils, tweet_utils, time_utils
import openspaces.secrets as s
from openchat.settings import BASE_DIR

#loggly = logging.getLogger('loggly')


class StreamListener(tweepy.StreamListener):
    """Object that defines the callback actions passed to tweepy.Stream"""
    def __init__(self, streambot, api=None):
        self.api = api or API()
        # needed ref to streambot so method can be called
        self.streambot = streambot
        self.tw_bot_id = 841013993602863104
        self.ignored_users = []
        
    def update_ignore_users(self):
        """Check app config table to get list of ignored twitter ids"""
        ignore_list = db_utils.get_ignored_users()
        ignore_list.append(self.tw_bot_id)
        self.ignored_users = ignore_list

    def on_status(self, status):
        """Take a tweet with matching keyword save and trigger retweet_logic"""
        
        self.update_ignore_users()

        if status.user.id in self.ignored_users:
            print("tweet from ignored user: {}".format(status.user.screen_name))
            #loggly.info("tweet recived from igonred user: {}".format(status.user.id))
            return

        # create or update user and tweet records in Django models
        db_utils.get_or_create_user_and_tweet(status)

        # trigger logic to handle tweet and decide on response in Streambot
        self.streambot.loadtest_logic(status.text, status.id_str, 
                                     status.user.screen_name, status.user.id)  
        
    def on_error(self, status_code):
        if status_code == 420:
            #loggly.error("error with tweepy, bot is down! status code: 420")
            print("bot is down with 420 status code from Twitter")
            return False


class Streambot:
    """Stream Twitter and look for tweets that contain targeted words,
    when tweets found look for datetime and room, if present save tweet
    to OutgoingTweet model.
    Ex.
    bot = Streambot()
    # to run a stream looking for tweets about PyCon
    bot.run_stream(["PyCon"])
    """
    def __init__(self):
        db_utils.setup_outgoing_config() # needs an outgoing config obj to check against
        self.api = self.setup_auth()
        self.stream_listener = StreamListener(self)
        jar_files = os.path.join(BASE_DIR, "python-sutime", "jars") 
        self.sutime = SUTime(jars=jar_files, mark_time_ranges=True)
        self.slacker = Slacker(s.SLACK_TOKEN)

    def setup_auth(self):
        """Set up auth stuff for api and return tweepy api object"""
        auth = tweepy.OAuthHandler(s.sender["CONSUMER_KEY"], 
                                   s.sender["CONSUMER_SECRET"])
        auth.set_access_token(s.sender["ACCESS_TOKEN"], 
                              s.sender["ACCESS_TOKEN_SECRET"])

        api = tweepy.API(auth)
        return api

    def run_stream(self, search_list=None):
        """Start stream, when matching tweet found on_status method called. 
        search_list arg is a list of terms that will be looked for in tweets
        """
        if search_list == None:
            raise ValueError("Need a list of search terms as arg to run_stream")

        stream = tweepy.Stream(auth=self.api.auth, listener=self.stream_listener)
        stream.filter(track=search_list)

    def send_mention_tweet(self, screen_name, room, time):
        """Mention a user in a tweet from bot letting them know that
        their tweet has been recieved and that we will send out reminders
        about their event.
        """
        mention = "@{} saw your openspaces tweet for: room {} at {}. Times should be relative to US/Pacific"
        mention = mention.format(screen_name, room, time)
        self.api.update_status(status=mention)

    def parse_time_room(self, tweet):
        """Get time and room number from a tweet using SUTime and tweet_utils"""
        extracted_time = self.sutime.parse(tweet)
        time_and_room = tweet_utils.get_time_and_room(tweet, extracted_time)
        return time_and_room

    def loadtest_logic(self, tweet, tweet_id, screen_name, user_id):
        """Logic similar to what is being used in the real bot so that we can 
        load test how much volume it can handle before twitter kicks it off 
        """
        # use SUTime to parse a datetime out of tweet
        time_room = self.parse_time_room(tweet)

        # fake time in the future that imitates a event's start time
        local_tz = pytz.timezone('US/Pacific')
        sample_time = datetime.datetime.now(local_tz) + datetime.timedelta(minutes=10)
        sample_time = sample_time.strftime("%Y-%m-%d %H:%M:%S")

        converted_time = time_utils.convert_to_utc(sample_time)
        room = "r123"

        # check for a time and room conflict, only 1 set of retweets per event
        conflict = db_utils.check_time_room_conflict(converted_time, room)

        # send message to slack when a tweet is scheduled to go out
        # slack_message = "{} From: {}, id: {}".format(tweet, screen_name, user_id)
        # self.slacker.chat.post_message('#loadtest_tweets', slack_message)

        # This record lets us check that retweets not for same event
        db_utils.create_event(description=tweet,
                              start=converted_time,
                              location=room,
                              creator=screen_name)

        tweet_utils.loadtest_schedule_tweets(screen_name, tweet, tweet_id, converted_time)
        print("tweet scheduled for retweet: {}".format(tweet))



if __name__ == '__main__':
    bot = Streambot()
    bot.run_stream(["hotdog", "puppies"])
    # keyword = "Python"
    # print(keyword)
    # looking = True

    # while looking:
    #     sentence = input("enter a fake tweet: ")

    #     if sentence == "quit":
    #         looking = False
    #     else:
    #         output = bot.parse_time_room(sentence)
    #         print(output)

