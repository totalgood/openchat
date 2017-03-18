from django.test import TestCase, Client
import json
import re
from freezegun import freeze_time

from twote.models import OutgoingTweet, OutgoingConfig
from twote.tasks import beat_tweet_scheduler, tweeter
from twote.models_calendar import Event

class StrictViewTest(TestCase):
    """simple tests for strict endpoint"""

    fixtures = ["twote/fixtures/twote_fixture.json"]

    def setUp(self):
        self.c = Client()

    def get_request_helper(self, hashtag=None):
        if hashtag is not None:
            response = self.c.get("/twote/strict/?format=json&hashtag={}".format(hashtag))
        else:
            response = self.c.get("/twote/strict/?format=json")
        return json.loads(response.content)

    def test_bad_endpoint_returns_404(self):
        response = self.c.get("/badendpoint/")
        self.assertEqual(response.status_code, 404)

    def test_bad_query_param_return_default_response(self):
        response = self.c.get("/twote/strict/?format=json&badparam=bad")

    def test_get_request_sends_200(self):
        response = self.c.get("/twote/strict/")
        self.assertEqual(response.status_code, 200)

    def test_each_tweet_only_has_one_hashtag(self):
        response = self.get_request_helper()
        hashtags = [tweet["tags"] for tweet in response["results"]]

        self.assertEqual(len(response["results"]), len(hashtags))

    def test_specific_hashtag_query_returns_correct_hashtags(self):
        response = self.get_request_helper("basicincome")
        hashtag = [tweet["tags"] for tweet in response["results"]]

        self.assertEqual(len(hashtag), 1)
        self.assertEqual(hashtag[0], "basicincome")

    def test_no_URLs_in_tweets(self):
        response = self.get_request_helper()
        tweet_text = [tweet["text"] for tweet in response["results"]]

        url_regex = '((http[s]?|ftp):\/)?\/?([^:\/\s]+)((\/\w+)*\/)([\w\-\.]+[^#?\s]+)(.*)?(#[\w\-]+)?'
        matched_tweets = [re.match(url_regex, tweet) for tweet in tweet_text]

        for match in matched_tweets:
            self.assertEqual(match, None)


class TestOutBoundTweetsEndpoint(TestCase):
    """
    Tests of endpoint filtering for pending tweets and tests of OutgoingTweet
    model's save method and coresponding celery tasks. For these tests to work
    properly you must have 'CELERY_ALWAYS_EAGER = True' in hackor/hackor/settings.py
    """
    fixtures = ["outgoing_fixture"]

    def setUp(self):
        self.c = Client()

    def api_call(self, url):
        response = self.c.get(url)
        json_response = json.loads(response.content.decode('utf-8'))
        return json_response

    def test_get_sends_200(self):
        response = self.c.get("/twote/tweets/?format=json")
        self.assertEqual(response.status_code, 200)

    def test_filter_tweets_by_approved_field(self):
        json_response = self.api_call("/twote/tweets/?approved=1&format=json")
        # 6 tweets in fixture are approved
        self.assertEqual(json_response["count"], 6)

    def test_filter_tweets_waiting_to_be_sent(self):
        json_response = self.api_call("/twote/tweets/?pending=True&format=json")
        # 4 pending tweets in fixture
        self.assertEqual(json_response["count"], 4)

    def test_filtering_tweets_with_both_query_params(self):
        json_one = self.api_call("/twote/tweets/?pending=True&approved=0&format=json")
        json_two = self.api_call("/twote/tweets/?approved=0&pending=True&format=json")
        self.assertEqual(json_one, json_two)
        # 2 tweets in fixture match query
        self.assertEqual(json_one["count"], 2)


class TestTweetModelSaveMethod(TestCase):
    """
    Test to check that model calcs the scheduled_time field when a tweet
    object is approved to be sent.
    """

    def setUp(self):
        OutgoingConfig.objects.create(auto_send=True, default_send_interval=1)

    def test_approved_tweet_gets_scheduled_time_auto_calculated(self):
        OutgoingTweet.objects.create(tweet="test tweet", approved=1)
        my_tweet = OutgoingTweet.objects.get(tweet="test tweet")

        self.assertEqual(bool(my_tweet.scheduled_time), True)

    def test_non_approved_tweet_gets_no_scheduled_time(self):
        OutgoingTweet.objects.create(tweet="non approved tweet", approved=0)
        pending_tweet = OutgoingTweet.objects.get(tweet="non approved tweet")

        self.assertEqual(bool(pending_tweet.scheduled_time), False)

    def test_tweet_gets_schedulec_time_when_approved_set_to_true(self):
        """
        A tweet object is created and is pending approval, later it is changed
        to approved and has it's scheduled time is calculated when approved.
        A tweets scheduled time will only be calculated when the model's save
        method is called.
        """
        pending_tweet = OutgoingTweet.objects.create(tweet="pending tweet", approved=0)
        self.assertEqual(bool(pending_tweet.scheduled_time), False)

        # pending_tweet is approved by user
        pending_tweet.approved = 1
        pending_tweet.save()

        self.assertEqual(bool(pending_tweet.scheduled_time), True)


class TestCeleryTasks(TestCase):
    """
    Check that the celery tasks perform as expected in isolation
    """

    def setUp(self):
        OutgoingConfig.objects.create(auto_send=True, default_send_interval=1)

    @freeze_time("2017-03-03")
    def test_beat_tweet_scheduler_schedules_correct_tweets(self):
        """
        Test that a tweet scheduled to be sent within the beat_tweet_scheduler
        time range is scheduled and added its task_scheduled flag is set to True
        """
        OutgoingTweet.objects.create(tweet="test time tweet", approved=1)

        # task is wating to be scheduled in DB so task_scheduled flag = False
        pre_scheduled = OutgoingTweet.objects.get(tweet="test time tweet")
        self.assertEqual(pre_scheduled.task_scheduled, False)

        beat_tweet_scheduler()

        post_scheduled = OutgoingTweet.objects.get(tweet="test time tweet")
        self.assertEqual(post_scheduled.task_scheduled, True)

    @freeze_time("2017-03-03")
    def test_tweeter_sends_tweet_and_sets_field(self):
        """
        Test that tweeter task sends tweet and writes sent time to Tweet obj
        """
        # create tweet to be sent
        outgoing = OutgoingTweet.objects.create(tweet="tweet in tweeter", approved=1, 
                                         task_scheduled=True)
        self.assertEqual(bool(outgoing.sent_time), False)

        tweeter(outgoing.tweet, outgoing.id)

        sent = OutgoingTweet.objects.get(pk=outgoing.id)
        self.assertEqual(bool(sent.sent_time), True)

class TestEventModel(TestCase):
    """Testcase to test the Event Model"""

    def setUp(self):
        self.e_norm = Event(
            title='event number 1',
            description='event for python people',
            start= timezone.now(),
            end= timezone.now()+timezone.timedelta(hours=2),
            location='Room 5'
        )

        self.e_no_end = Event(
            title='event number 2',
            description='another event for python people',
            start= timezone.now()+timezone.timedelta(hours=2),
            location='Room 6'
        )

        self.e_bad_end = self.e2 = Event(
            title='event number 2',
            description='another event for python people',
            start=timezone.now()+timezone.timedelta(hours=2),
            end=timezone.now()+timezone.timedelta(hours=1),
            location='Room 6'
        )

    def test_can_create_event(self):
        old_count = Event.objects.count()
        self.e_norm.save()
        new_count = Event.objects.count()
        self.assertNotEqual(old_count, new_count)

    def test_default_end_time(self):
        self.e_no_end.save()
        self.assertEqual(self.e_no_end.end, self.e_no_end.start+timezone.timedelta(hours=1))

    def test_bad_end_time(self):
        self.time_diff = self.e_bad_end.end - self.e_bad_end.start
        with self.assertRaises(ValidationError) as ex:
            self.e_bad_end.save()

    def test_update_last_updated(self):
        old_time = self.e_norm.last_updated
        self.e_norm.title = 'blah'
        self.e_norm.save()
        new_time = self.e_norm.last_updated
        self.assertNotEqual(old_time, new_time)

