import datetime
from django.test import TestCase
from freezegun import freeze_time
import mock

from openspaces.tasks import beat_tweet_scheduler, tweeter
from openspaces.models import OutgoingConfig, OutgoingTweet

class TestCeleryTasks(TestCase):
    """
    Check that the celery tasks perform as expected in isolation 
    """
    def setUp(self):
        OutgoingConfig.objects.create(auto_send=True, 
                                    default_send_interval=1, 
                                    ignore_users=[12345,])

    @freeze_time("2017-08-05")
    def outgoing_tweet_helper(self):
        OutgoingTweet.objects.create(
                                    tweet="a test tweet",
                                    approved=1,
                                    scheduled_time=datetime.datetime.now(),
                                    original_tweet="fake original tweet",
                                    screen_name="fake_screen_name"
                                    )

    @freeze_time("2017-08-05")
    @mock.patch("openspaces.tasks.tweeter.apply_async")
    def test_beat_tweet_scheduler_works_as_expected(self, fake_tweeter):
        self.outgoing_tweet_helper()
        beat_tweet_scheduler()
        self.assertEqual(fake_tweeter.call_count, 1)

        scheduled_flag_check = OutgoingTweet.objects.first()
        self.assertEqual(scheduled_flag_check.task_scheduled, 1)

    @mock.patch("openspaces.tasks.tweepy_send_tweet")
    def test_tweeter_calls_tweepy_send_tweet(self, fake_sender):
        tweeter("fake tweet", 1234)
        self.assertEqual(fake_sender.call_count, 1)
        
