from __future__ import absolute_import, unicode_literals
from datetime import datetime, timedelta
from celery.decorators import periodic_task

from openspaces.tweepy_connect import tweepy_send_tweet, tweepy_send_test_tweet
from openspaces.models import OutgoingTweet, OutgoingConfig
from openchat.celery import app 

@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Set up periodic tasks with beat after app is finalized and loaded 
    """
    # beat task that runs every 30 seconds and calls beat_tweet_scheduler
    sender.add_periodic_task(30.0, beat_tweet_scheduler.s(), 
                            name='check db for pending tweets')

@app.task
def beat_tweet_scheduler():
    """
    Check for tweets to be sent within next minute, add send task to queue  
    """ 
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(minutes=1)
    tweets = OutgoingTweet.objects.filter(sent_time__isnull=True) \
                          .filter(approved__exact=1) \
                          .filter(task_scheduled__exact=False) \
                          .filter(scheduled_time__range=(start_time, end_time)) 

    # schedule tweeter task and then set tweet task_scheduled field to True
    for tweet in tweets:
        tweeter.apply_async((tweet.tweet, tweet.id), eta=tweet.scheduled_time)
        OutgoingTweet.objects.filter(pk=tweet.id).update(task_scheduled=True)

@app.task(
    bind=True,
    max_retries=3,
    soft_time_limit=5, 
    # ignore_result=True
)
def tweeter(self, tweet, id):
    """
    Write sent_time to tweet instance in model and send tweet with tweepy
    """ 
    time_sent = datetime.utcnow()
    OutgoingTweet.objects.filter(pk=id).update(sent_time=time_sent)

    # TODO switch this back on when running real thing
    # tweepy_send_tweet(tweet)
    tweepy_send_test_tweet(tweet)

