import tweepy
from openspaces.secrets import openspaces


def get_api():
    auth = tweepy.OAuthHandler(openspaces["CONSUMER_KEY"], openspaces["CONSUMER_SECRET"])
    auth.set_access_token(openspaces["ACCESS_TOKEN"], openspaces["ACCESS_TOKEN_SECRET"])
    return tweepy.API(auth)

def tweepy_send_tweet(tweet):
    api = get_api()
    status = api.update_status(status=tweet)
    return None
