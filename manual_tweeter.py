import datetime
import random
import string
from threading import Thread
import pytz
import tweepy
from tweepy.api import API
import openspaces.secrets as s


class Tweeter:
    """Helper class to send tweets that will be picked up by load_test_bot"""
    def __init__(self):
        self.api = self.setup_auth()

    def setup_auth(self):
        """Set up auth stuff for api and return tweepy api object"""
        auth = tweepy.OAuthHandler(s.sender["CONSUMER_KEY"],
                                   s.sender["CONSUMER_SECRET"])
        auth.set_access_token(s.sender["ACCESS_TOKEN"],
                              s.sender["ACCESS_TOKEN_SECRET"])

        api = tweepy.API(auth)
        return api

    def send_tweet(self, hashtag, room_num=None, room=False):
        tweet = f"test tweet #{hashtag} "

        if room:
            local_tz = pytz.timezone('US/Eastern')
            sample_time = datetime.datetime.now(local_tz) + datetime.timedelta(minutes=45)
            sample_time = sample_time.strftime("%H:%M")
            tweet += f"room {room_num} today at {sample_time}"

        self.api.update_status(status=tweet)


def hashtag_gen(size=8):
    "generate a random hashtag for bot testing"
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

def room_num_gen():
    return "a" + "".join(str(random.randint(0,9)) for _ in range(3))


if __name__ == '__main__':
    hashtag = hashtag_gen()
    tweeter = Tweeter()
    print(hashtag)

    looking = True

    while looking:
        tweet = input("Type: quit, tweet room, tweet plain\n")

        if tweet == "quit":
            looking = False

        elif tweet == "tweet room":
            room_num = room_num_gen()
            tweeter.send_tweet(hashtag, room_num, True)

        elif tweet == "tweet plain":
            tweeter.send_tweet(hashtag)

        else:
            print("invalid choice")
            #bot.loadtest_logic(tweet, random.randint(0, 50000), "blarg", random.randint(0, 50000))
