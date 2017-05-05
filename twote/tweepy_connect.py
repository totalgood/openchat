import tweepy
from twote.secrets import listener


def get_api():
    auth = tweepy.OAuthHandler(listener["CONSUMER_KEY"], listener["CONSUMER_SECRET"])
    auth.set_access_token(listener["ACCESS_TOKEN"], listener["ACCESS_TOKEN_SECRET"])
    return tweepy.API(auth)

def tweepy_send_tweet(tweet):
    api = get_api()
    status = api.update_status(status=tweet)
    return None
