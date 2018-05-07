import datetime
import django
import os
import re

import random
import string
from threading import Thread

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
from slack_msg import send_slack_message

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
            return

        # create or update user and tweet records in Django models
        db_utils.get_or_create_user_and_tweet(status)

        # trigger logic to handle tweet and decide on response in Streambot
        self.streambot.retweet_logic(status.text, status.id_str,
                                     status.user.screen_name, status.user.id)

    def on_error(self, status_code):
        if status_code == 420:
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
        auth = tweepy.OAuthHandler(s.test_bot["CONSUMER_KEY"],
                                   s.test_bot["CONSUMER_SECRET"])
        auth.set_access_token(s.test_bot["ACCESS_TOKEN"],
                              s.test_bot["ACCESS_TOKEN_SECRET"])

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

    def value_check(self, time_room_obj):
        """Returns a tuple with the counts of values extracted from a tweet
        in the parse_time_room method. This tuple is used to decide how bot
        will respond to tweet.
        """
        num_room_values = len(time_room_obj["room"])
        num_time_values = len(time_room_obj["date"])

        return (num_room_values, num_time_values)

    def parse_time_room(self, tweet):
        """Get time and room number from a tweet using SUTime and tweet_utils"""
        extracted_time = self.sutime.parse(tweet)
        time_and_room = tweet_utils.get_time_and_room(tweet, extracted_time)
        return time_and_room

    def retweet_logic(self, tweet, tweet_id, screen_name, user_id):
        """Use SUTime to try to parse a datetime out of a tweet, if successful
        save tweet to OutgoingTweet to be retweeted
        """
        # use SUTime to parse a datetime out of tweet
        time_room = self.parse_time_room(tweet)

        # make sure both time and room extracted and only one val each
        val_check = self.value_check(time_room)

        if val_check == (1, 1):
            room = time_room["room"][0]
            date_mention = tweet_utils.check_date_mention(tweet)
            converted_time = time_utils.convert_to_utc(time_room["date"][0],
                                                       date_mention)

            # check for a time and room conflict, only 1 set of retweets per event
            # default time range that a room is resrved for is -15 +30 mins
            conflict = db_utils.check_time_room_conflict(converted_time, room)

            if not conflict:
                # TODO make sure event obj is passed in to schedule_tweets in the real Streambot
                event_obj = db_utils.create_event(description=tweet,
                                                  start=converted_time,
                                                  location=room,
                                                  creator=screen_name)

                tweet_utils.schedule_tweets(screen_name, tweet, tweet_id,
                                            converted_time, event_obj)

                slack_msg = "{} From: {}, id: {}".format(tweet, screen_name, user_id)
                # self.send_slack_message('#outgoing_tweets', slack_message)

                send_slack_message(user_id=user_id,
                                   tweet_id=tweet_id,
                                   screen_name=screen_name,
                                   tweet_created=True,
                                   tweet=tweet,
                                   slack_msg=slack_msg)

                self.send_mention_tweet(screen_name, room, converted_time)

            else:
                message = """Tweet recived for an event bot is already scheduled
                    to retweet about. Sender: {}, room: {}, time: {},
                    tweet: {} tweet_id: {}
                    """
                # message = message.format(screen_name, room, converted_time, tweet, tweet_id)
                # self.send_slack_message("#event_conflict", message)

        elif val_check == (0, 0):
            # tweet found but without valid time or room extracted, ignore
            pass

        else:
            # tweet with relevant information but not exactly 1 time & 1 room
            slack_msg = """Tweet found that needs review: {}  tweet_id: {} screen_name: {}, user_id: {}"""
            slack_msg = slack_msg.format(tweet, tweet_id, screen_name, user_id)
            # self.send_slack_message("#need_review", message)

            send_slack_message(user_id=user_id,
                               tweet_id=tweet_id,
                               screen_name=screen_name,
                               tweet_created=False,
                               tweet=tweet,
                               slack_msg=slack_msg)

    def loadtest_logic(self, tweet, tweet_id, screen_name, user_id):
        """Logic similar to what is being used in the real bot so that we can
        load test how much volume it can handle before twitter kicks it off
        """
        # use SUTime to parse a datetime out of tweet
        time_room = self.parse_time_room(tweet)

        # fake time in the future that imitates a event's start time
        local_tz = pytz.timezone('US/Eastern')
        sample_time = datetime.datetime.now(local_tz) + datetime.timedelta(minutes=10)
        sample_time = sample_time.strftime("%Y-%m-%d %H:%M:%S")

        event_time = time_utils.convert_to_utc(sample_time)
        print(event_time)
        room = random.randint(0, 3000)

        # check for a time and room conflict, only 1 set of retweets per event
        conflict = db_utils.check_time_room_conflict(event_time, room)

        if not conflict:
            # This record lets us check that retweets not for same event
            event_obj = db_utils.create_event(description=tweet,
                                              start=event_time,
                                              location=room,
                                              creator=screen_name)

            tweet_utils.loadtest_schedule_tweets(screen_name=screen_name,
                                                 tweet=tweet,
                                                 tweet_id=tweet_id,
                                                 event_time=event_time,
                                                 event_obj=event_obj)

            print("tweet scheduled for retweet: {}".format(tweet))

            slack_msg = "{} From: {}, id: {}".format(tweet, screen_name, user_id)
            # self.send_slack_message('#outgoing_tweets', slack_message)

            send_slack_message(user_id=user_id,
                               tweet_id=tweet_id,
                               screen_name=screen_name,
                               tweet_created=True,
                               tweet=tweet,
                               slack_msg=slack_msg,
                               event_obj=event_obj)

        else:
            print("conflict when scheduling the tweet")


if __name__ == '__main__':
    bot = Streambot()
    hashtag = input("Provide current hashtag: ")
    print(f"listening for: {hashtag}")
    bot.run_stream([hashtag])

    # bot.retweet_logic("tweet room a523 today at 10:05 am",
    #                   random.randint(0, 1000),
    #                   "screen name",
    #                   random.randint(0, 1000))

    # seeing java errors when running bot on diff thread
    # thread = Thread(target=bot.run_stream, args=([hashtag],))
    # thread.start()

    # looking = True
    # while looking:
    #     tweet = input("Type: quit, tweet room, tweet plain:\n")

    #     if tweet == "quit":
    #         looking = False
    #         thread.stop()

    #     elif tweet == "tweet room":
    #         tweeter.send_tweet(hashtag, True)

    #     elif tweet == "tweet plain":
    #         tweeter.send_tweet(hashtag, False)

    #     else:
    #         print("invalid option")
    #         #bot.loadtest_logic(tweet, random.randint(0, 50000), "blarg", random.randint(0, 50000))

