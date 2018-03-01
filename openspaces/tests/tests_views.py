from django.test import TestCase, Client
from rest_framework.test import APIRequestFactory

from openspaces.models import OutgoingTweet, OutgoingConfig, User
from openspaces.views import slack_interactive_endpoint


class TestSlackButtonInteractions(TestCase):
    """
    Test the interaction between slack buttons and the tweet model
    """

    def setUp(self):
        OutgoingConfig.objects.create(auto_send=True,
                                      default_send_interval=1,
                                      ignore_users=[])
        self.factory = APIRequestFactory()
        self.c = Client()

    def test_approve_tweet_works(self):
        OutgoingTweet.objects.create(tweet="test tweet", approved=1)
        my_tweet = OutgoingTweet.objects.get(tweet="test tweet")

        request = self.factory.post("/openspaces/slack/", {"hahah": "hahah"}, content_type="application/x-www-form-urlencoded")
        print(request)

        response = slack_interactive_endpoint(request)
        print(response)

        # response = self.c.post("/openspaces/slack/",)
        # print(response)

        # print(my_tweet.tweet)
        # print(my_tweet.approved)
        # print("HHHHHHHHHHHHHHHh")



