from django.test import TestCase, Client
import json


class StrictViewTest(TestCase):
    """simple tests for strict endpoint"""

    # need to build fitures for test DB and load here

    def setUp(self):
        self.c = Client()

    def get_request_helper(self, hashtag=None):
        if hashtag is not None:
            response = self.c.get('/twote/strict/?hashtag={}'.format(hashtag))
        else:
            response = self.c.get('/twote/strict/')
        return json.loads(response.content)

    def test_get_request_sends_200(self):
        response = self.c.get('/twote/strict/')
        self.assertEqual(response.status_code, 200)

    #def test_each_tweet_only_has_one_hashtag(self):
        #response = self.get_request_helper()
        #hashtags = [tweet["tags"] for tweet in response]

        #self.assertEqual(len(response), len(hashtags))
