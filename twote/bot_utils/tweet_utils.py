from datetime import timedelta
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
import re

from . import db_utils


def get_time_and_room(tweet, extracted_time):
    """Get room number from a tweet while ignoring the time that was extracted
    using SUTime. extracted_time should be equal to the object SUTime parsed 
    """
    result = {}
    result["date"] = []
    result["room"] = []

    tweet_without_time = tweet

    for time_slot in extracted_time:
        tweet_without_time = tweet_without_time.replace(time_slot["text"], "")
        result["date"].append(time_slot.get("value"))

    #filter_known_words = [word.lower() for word in word_tokenize(tweet_without_time) if word.lower() not in (stopwords.words('english') + nltk.corpus.words.words())]
    filter_known_words = [word.lower() for word in word_tokenize(tweet_without_time)]

    # regular expression for room
    room_re = re.compile("([a-zA-Z](\d{3})[-+]?(\d{3})?)")

    for word in filter_known_words:
        if room_re.match(word):
            result["room"].append(room_re.match(word).group())

    return result

def schedule_tweets(u_name, tweet, t_id, talk_time, num_tweets=2, interval=1):
    """Schedule reminder tweets at set intervals. num_tweets controls
    the number of remindertweets sent and interval controls the minutes
    before the event the tweets are sent. 

    Ex. 
    num_tweets = 2 & interval = 15 
    will send 2 tweets 30 & 15 mins before event
    """
    # check config table to see if autosend on
    approved = db_utils.check_for_auto_send()

    tweet_url = "https://twitter.com/{name}/status/{tweet_id}"
    embeded_tweet = tweet_url.format(name=u_name, tweet_id=t_id)

    for mins in range(interval,(num_tweets*interval+1), interval):
        remind_time = talk_time - timedelta(minutes=mins)
        message = "Coming up in {} minutes! {}".format(mins, embeded_tweet)

        tweet_obj = {
            "message": message,
            "approved": approved,
            "remind_time": remind_time
        }

        db_utils.save_outgoing_tweet(tweet_obj)
