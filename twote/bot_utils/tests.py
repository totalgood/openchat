import datetime
from django.test import TestCase
from freezegun import freeze_time
import pytz

from twote.bot_utils import db_utils, tweet_utils, time_utils
from twote.models import OutgoingTweet, OutgoingConfig, RetweetEvent, User


class TestDBUtils(TestCase):
    """Test the utility funcs created to help bot interact with Django models"""

    def setUp(self):
        OutgoingConfig.objects.create(auto_send=True, 
                                default_send_interval=1, ignore_users=[12345,])

    def test_get_ignored_users_returns_correct_list(self):
        ignore_list = db_utils.get_ignored_users()
        self.assertEqual(ignore_list, [12345, ])

    def test_check_for_auto_send_returns_auto_send_flag(self):
        auto_send_flag = db_utils.check_for_auto_send()
        self.assertEqual(auto_send_flag, 1)
    
    @freeze_time("2017-08-05")
    def test_save_outgoing_tweet_func_saves_correctly(self):
        tweet_obj = {
            "message": "a test tweet",
            "approved": 1,
            "remind_time": datetime.datetime.now()
        }

        tweets_before_save = OutgoingTweet.objects.all()
        self.assertEqual(len(tweets_before_save), 0)

        db_utils.save_outgoing_tweet(tweet_obj)

        tweets_after_save = OutgoingTweet.objects.all()
        self.assertEqual(len(tweets_after_save), 1)

    @freeze_time("2017-08-05")
    def test_event_conflict_check_works_correctly(self):
        """Check that conflict check returns correct T/F based on matches"""

        time_delt = datetime.timedelta(1)
        fake_now = datetime.datetime.now()
        fake_user = User.objects.create(id_str=12345)
        fake_loc = "B123"

        RetweetEvent.objects.create(
                            description="a fake description",
                            start=fake_now, 
                            location=fake_loc,
                            creator=fake_user
                            )

        diff_time = db_utils.check_time_room_conflict(fake_now - time_delt, fake_loc)
        self.assertFalse(diff_time)

        diff_room = db_utils.check_time_room_conflict(fake_now, "Z123")
        self.assertFalse(diff_room)

        match = db_utils.check_time_room_conflict(fake_now, fake_loc)
        self.assertTrue(match)

    @freeze_time("2017-08-05")
    def test_update_time_and_room_utils_works(self):
        no_records = RetweetEvent.objects.all()
        self.assertEqual(len(no_records), 0)

        # make call to utils func to create a db record
        db_utils.create_event(
                              start=datetime.datetime.now(),
                              creator="fakeusername",
                              location="B123",
                              description="a fake tweet used in description"
                             )

        should_be_one = RetweetEvent.objects.all()
        self.assertEqual(len(should_be_one), 1)


class TestTweetUtils(TestCase):
    """Test that the Tweet utils funcs behave as expected in isolation"""

    def test_get_time_and_room_correctly_returns_time_room_obj(self):
        tweet = "a test tweet R123 2:05pm"

        # what SUTime returns when it parses time in tweet
        extracted_time = [
                            {
                            'type': 'TIME', 
                            'end': 24, 
                            'text': '2:05pm', 
                            'value': '2017-04-11T14:05', 
                            'start': 18
                            }
                          ]
        expected_output = {'room': ['r123'], 'date': ['2017-04-11T14:05']}

        result = tweet_utils.get_time_and_room(tweet, extracted_time)
        self.assertEqual(result, expected_output)

    @freeze_time("2017-08-05")
    def test_schedule_tweets_saves_legit_tweets_to_db(self):
        # need to setup a fake app config object
        OutgoingConfig.objects.create(auto_send=True, 
                                default_send_interval=1, 
                                ignore_users=[12345,])

        # building args for schedule tweets
        screen_name = "tw_testy"
        tweet = "a test tweet"
        tweet_id = 123456
        talk_time = datetime.datetime.now()

        tweets_in_db_before = OutgoingTweet.objects.all()
        self.assertEqual(len(tweets_in_db_before), 0)

        tweet_utils.schedule_tweets(screen_name, tweet, tweet_id, talk_time)

        tweets_in_db_after = OutgoingTweet.objects.all()
        self.assertEqual(len(tweets_in_db_after), 2)


class TestTimeUtils(TestCase):
    """Tests of the time utils used in bot"""

    @freeze_time("2017-08-05")
    def test_convert_to_utc_returns_correct_time(self):
        time_str_from_sutime = "2017-04-11T08:00"
        converted_time = time_utils.convert_to_utc(time_str_from_sutime)

        utc = pytz.utc
        expected_output = datetime.datetime(2017, 8, 4, 15, tzinfo=utc) 

        self.assertEqual(converted_time, expected_output)
