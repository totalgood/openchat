# These test must be run manually by switching CELERY_ALWAYS_EAGER = True
# in the settings file.


# class TestCeleryTasks(TestCase):
#     """
#     Check that the celery tasks perform as expected in isolation 
#     """

    # def setUp(self):
    #     OutgoingConfig.objects.create(auto_send=True, default_send_interval=1)

    # @freeze_time("2017-03-03")
    # def test_beat_tweet_scheduler_schedules_correct_tweets(self):
    #     """
    #     Test that a tweet scheduled to be sent within the beat_tweet_scheduler
    #     time range is scheduled and added its task_scheduled flag is set to True
    #     """
    #     OutgoingTweet.objects.create(tweet="test time tweet", approved=1)

    #     # task is wating to be scheduled in DB so task_scheduled flag = False
    #     pre_scheduled = OutgoingTweet.objects.get(tweet="test time tweet")
    #     self.assertEqual(pre_scheduled.task_scheduled, False)

    #     beat_tweet_scheduler()

    #     post_scheduled = OutgoingTweet.objects.get(tweet="test time tweet")
    #     self.assertEqual(post_scheduled.task_scheduled, True)

    # @freeze_time("2017-03-03")
    # def test_tweeter_sends_tweet_and_sets_field(self):
    #     """
    #     Test that tweeter task sends tweet and writes sent time to Tweet obj
    #     """
    #     # create tweet to be sent
    #     outgoing = OutgoingTweet.objects.create(tweet="tweet in tweeter", approved=1, 
    #                                      task_scheduled=True)
    #     self.assertEqual(bool(outgoing.sent_time), False)

    #     tweeter(outgoing.tweet, outgoing.id)

    #     sent = OutgoingTweet.objects.get(pk=outgoing.id)
    #     self.assertEqual(bool(sent.sent_time), True)
    