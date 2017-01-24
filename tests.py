from django.test import TestCase, Client
import json
import re


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
