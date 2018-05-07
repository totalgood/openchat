from datetime import datetime, timedelta
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
import re
import string

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

def find_valid_rooms(words):
    """Check to make sure a room mention is only one of the rooms available
    for pycon openspaces, totally just a quick work around for pycon
    """
    # drop punctuation
    words = " ".join(words)
    exclude = set(string.punctuation)
    exclude.discard("+")
    words = "".join(ch for ch in words if ch not in exclude).split()

    #lower case because all words lowered in time and room func
    valid_rooms = [
        "a105+a106", "a107+a108", "b110+111", "b112",
        "b113", "b114", "b115", "b116", "b117"
    ]
    return [room for room in words if room in valid_rooms]

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

    # regular expression for room, allows any 3 num combo following "a" or "b"
    room_re = re.compile("([a-bA-B](\d{3})[-+]?[aA]?(\d{3})?)")

    for word in filter_known_words:
        if room_re.match(word):
            result["room"].append(room_re.match(word).group())

    # super strict, only allows rooms exactly as seen on board 
    # result["room"] = find_valid_rooms(filter_known_words)

    # using clean_times to drop any year mentions in tweet
    result["date"] = clean_times(result["date"])

    return result

# TODO make sure that the event_obj is supplied in streambot.py & possibly merge this func with schedule_slack_tweets
def schedule_tweets(u_name, tweet, t_id, talk_time, event_obj=None, num_tweets=1, interval=15):
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
        # #PyConOpenSpace add this back into message when done testing
        message = "Coming up in {} minutes! {}".format(mins, embeded_tweet)

        db_utils.save_outgoing_tweet(tweet=message,
                                     tweet_id=t_id,
                                     approved=approved,
                                     scheduled_time=remind_time,
                                     original_tweet=tweet,
                                     screen_name=u_name,
                                     event_obj=event_obj)

def schedule_slack_tweets(**kwargs):
    """
    Schedule a tweet to be sent out once it is user approved in slack
    """
    num_tweets = 1
    interval = 15

    tweet_url = "https://twitter.com/{name}/status/{tweet_id}"
    embeded_tweet = tweet_url.format(name=kwargs["screen_name"], tweet_id=kwargs["tweet_id"])

    for mins in range(interval,(num_tweets*interval+1), interval):
        remind_time = kwargs["event_time"] - timedelta(minutes=mins)
        # #PyConOpenSpace add this back into message when done testing
        message = "Coming up in {} minutes! {}".format(mins, embeded_tweet)

        # TODO add the updated tweet_id field to this object when it's saved
        db_utils.save_outgoing_tweet(tweet=message,
                                     tweet_id=kwargs["tweet_id"],
                                     approved=kwargs["approved"],
                                     scheduled_time=remind_time,
                                     original_tweet=kwargs["tweet"],
                                     screen_name=kwargs["screen_name"],
                                     event_obj=kwargs["event_obj"])

def loadtest_schedule_tweets(**kwargs):
    """
    Func used during loadtesting to simulate a retweet without using any
    of the original senders content
    """
    num_tweets = 1
    interval = 15

    # check config table to see if autosend on
    approved = db_utils.check_for_auto_send()

    # tweet_url = "https://twitter.com/{name}/status/{tweet_id}"
    # embeded_tweet = tweet_url.format(name=u_name, tweet_id=t_id)

    for mins in range(interval,(num_tweets*interval+1), interval):
        remind_time = kwargs["event_time"] - timedelta(minutes=mins)
        message = "fake tweet about a event! {}".format(datetime.utcnow())

        db_utils.save_outgoing_tweet(tweet=message,
                                     tweet_id=kwargs["tweet_id"],
                                     approved=approved,
                                     scheduled_time=remind_time,
                                     original_tweet=kwargs["tweet"],
                                     screen_name=kwargs["screen_name"],
                                     event_obj=kwargs["event_obj"])
