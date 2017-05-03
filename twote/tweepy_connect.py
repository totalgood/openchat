import tweepy
from secrets import sender


def get_api():
    auth = tweepy.OAuthHandler(sender.TEST_CONSUMER_KEY, sender.TEST_CONSUMER_SECRET)
    auth.set_access_token(sender.TEST_ACCESS_TOKEN, sender.TEST_ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)

def tweepy_send_tweet(tweet):
    api = get_api()
    status = api.update_status(status=tweet)
    return None
