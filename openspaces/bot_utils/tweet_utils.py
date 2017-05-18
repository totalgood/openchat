from datetime import datetime, timedelta
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
import re

from . import db_utils, time_utils


def clean_times(extracted_time):
    """Clean any time values that are just years.
    Quick fix to stop bot grabbing 2017 off of #PyCon2017
    """
    year_pattern = re.compile("\d{4}$")
    cleaned_times = [time for time in extracted_time if not year_pattern.match(time)]
    return cleaned_times

def check_date_mention(tweet):
    """Check the tweet to see if there is a valid date mention for the 
    three dates of pyconopenspaces: 5/19, 5/20, 5/21. Quick fix to override 
    SUTime defaulting to today's date and missing numeric info about event's date
    """
    date_pat = re.compile("([5]{1}\/\d{2})")
    valid_dates = ["5/19", "5/20", "5/21"]
    dates = [d for d in tweet.split() if date_pat.match(d) and d in valid_dates]
    return dates if len(dates) == 1 else False

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

def schedule_tweets(u_name, tweet, t_id, talk_time, num_tweets=1, interval=15):
    """Schedule reminder tweets at set intervals. num_tweets controls
    the number of remindertweets sent and interval controls the minutes
    before the event the tweets are sent. 

    Ex. 
    num_tweets = 2 & interval = 15 
    will send 2 tweets 30 & 15 mins before event
    """
    # check config table to see if autosend on
    approved = db_utils.check_for_auto_send()

    within_30_mins = time_utils.check_start_time(talk_time)
    
    if within_30_mins:
        approved = 0

    tweet_url = "https://twitter.com/{name}/status/{tweet_id}"
    embeded_tweet = tweet_url.format(name=u_name, tweet_id=t_id)

    for mins in range(interval,(num_tweets*interval+1), interval):
        remind_time = talk_time - timedelta(minutes=mins)
        message = "Coming up in {} minutes! {}".format(mins, embeded_tweet)

        db_utils.save_outgoing_tweet(
                                    tweet=message,
                                    approved=approved,
                                    scheduled_time=remind_time,
                                    original_tweet=tweet,
                                    screen_name=u_name
                                    )

def loadtest_schedule_tweets(u_name, tweet, t_id, talk_time, num_tweets=1, interval=1):
    """Func used during loadtesting to simulate a retweet without using any 
    of the original senders content
    """
    # check config table to see if autosend on
    approved = db_utils.check_for_auto_send()

    # tweet_url = "https://twitter.com/{name}/status/{tweet_id}"
    # embeded_tweet = tweet_url.format(name=u_name, tweet_id=t_id)

    for mins in range(interval,(num_tweets*interval+1), interval):
        remind_time = talk_time - timedelta(minutes=mins)
        message = "fake tweet about a event! {}".format(datetime.utcnow())

        db_utils.save_outgoing_tweet(
                                    tweet=message,
                                    approved=approved,
                                    scheduled_time=remind_time,
                                    original_tweet=tweet,
                                    screen_name=u_name
                                    )
