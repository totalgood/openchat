from django.test import TestCase, Client
from rest_framework.test import APIRequestFactory

from openspaces.models import OutgoingTweet, OutgoingConfig, User
from openspaces.views import slack_interactive_endpoint

from urllib.parse import urlencode


fake_req = urlencode({"payload":"{\"type\":\"interactive_message\",\"actions\":[{\"name\":\"userA|1234\",\"type\":\"button\",\"value\":\"yes\"}],\"callback_id\":\"tweet_approval\",\"team\":{\"id\":\"T9F7509SA\",\"domain\":\"openchatworkspace\"},\"channel\":{\"id\":\"C9F750BQW\",\"name\":\"general\"},\"user\":{\"id\":\"U9E8N863D\",\"name\":\"zak.kent\"},\"action_ts\":\"1519876105.992936\",\"message_ts\":\"1519876102.000134\",\"attachment_id\":\"1\",\"token\":\"FeEeQVrJJcMUDCEScbYO5MM5\",\"is_app_unfurl\":false,\"original_message\":{\"text\":\"Do you approve this tweet?\",\"username\":\"openchat-bot\",\"bot_id\":\"B9EDN2LV9\",\"attachments\":[{\"callback_id\":\"tweet_approval\",\"fallback\":\"You are unable to appove a tweet\",\"id\":1,\"color\":\"3AA3E3\",\"actions\":[{\"id\":\"1\",\"name\":\"approval\",\"text\":\"Yes\",\"type\":\"button\",\"value\":\"yes\",\"style\":\"\"},{\"id\":\"2\",\"name\":\"approval\",\"text\":\"No\",\"type\":\"button\",\"value\":\"no\",\"style\":\"\"}]}],\"type\":\"message\",\"subtype\":\"bot_message\",\"ts\":\"1519876102.000134\"},\"response_url\":\"https:\\/\\/hooks.slack.com\\/actions\\/T9F7509SA\\/322619394691\\/zcYozvXJBb1y2BugNObgss38\",\"trigger_id\":\"322695558964.321243009894.7d2d538ad155f020d4241e42b2b21c41\"}"})


class TestSlackButtonInteractions(TestCase):
    """
    Test the interaction between slack buttons and the tweet model
    """

    def setUp(self):
        OutgoingConfig.objects.create(auto_send=True,
                                      default_send_interval=1,
                                      ignore_users=[])
        self.factory = APIRequestFactory()

    def test_approve_tweet_works(self):
        OutgoingTweet.objects.create(tweet="test tweet", approved=0)

        our_tweet = OutgoingTweet.objects.get(tweet="test tweet")
        print("first check", our_tweet.approved)
        self.assertEqual(our_tweet.approved, 0)

        request = self.factory.post("/openspaces/slack/", fake_req, content_type="application/x-www-form-urlencoded")


        response = slack_interactive_endpoint(request)

        changed_tweet = OutgoingTweet.objects.get(tweet="test tweet")
        print( "tweet approved: ", changed_tweet.approved)

        self.assertEqual(changed_tweet.approved, 1)

        self.assertEqual(response.status_code, 200)

