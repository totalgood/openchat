from datetime import datetime, timedelta, timezone
from django.test import TestCase
from freezegun import freeze_time
import pytz

from openspaces.bot_utils import db_utils, tweet_utils, time_utils
from openspaces.models import OutgoingTweet, OutgoingConfig, OpenspacesEvent, User


class TestDBUtils(TestCase):
    """Test the utility funcs created to help bot interact with Django models"""

    def setUp(self):
        OutgoingConfig.objects.create(auto_send=True, 
                                    default_send_interval=1, 
                                    ignore_users=[12345,])

    def test_get_ignored_users_returns_correct_list(self):
        ignore_list = db_utils.get_ignored_users()
        self.assertEqual(ignore_list, [12345, ])

    def test_check_for_auto_send_returns_auto_send_flag(self):
        auto_send_flag = db_utils.check_for_auto_send()
        self.assertEqual(auto_send_flag, 1)
    
    @freeze_time("2017-08-05")
    def test_save_outgoing_tweet_func_saves_correctly(self):
        tweets_before_save = OutgoingTweet.objects.all()
        self.assertEqual(len(tweets_before_save), 0)

        db_utils.save_outgoing_tweet(
                                    tweet="a test tweet",
                                    approved=1,
                                    scheduled_time=datetime.now(timezone.utc),
                                    original_tweet="fake original tweet",
                                    screen_name="fake_screen_name"
                                    )

        tweets_after_save = OutgoingTweet.objects.all()
        self.assertEqual(len(tweets_after_save), 1)

    @freeze_time("2017-08-05")
    def test_update_time_and_room_utils_works(self):
        no_records = OpenspacesEvent.objects.all()
        self.assertEqual(len(no_records), 0)

        # make call to utils func to create a db record
        db_utils.create_event(
                              start=datetime.now(timezone.utc),
                              creator="fakeusername",
                              location="B123",
                              description="a fake tweet used in description"
                             )

        should_be_one = OpenspacesEvent.objects.all()
        self.assertEqual(len(should_be_one), 1)


class TestDBRoomConflictUtile(TestCase):
    """Test that conflict check returns correct T/F based on matches 
    in time range. Default time range is -15 to +30 minutes of an 
    existing event. These values can be adjusted in bot when conflict
    check is called.
    """

    @freeze_time("2017-08-05T11:00")
    def setUp(self):
        self.now = datetime.now(timezone.utc)
        self.loc = "B123"
        fake_user = User.objects.create(id_str=12345)
        OpenspacesEvent.objects.create(
                            description="a fake description",
                            start=self.now, 
                            location=self.loc,
                            creator=fake_user
                            )

    def test_conflict_check_works_correctly_with_different_rooms(self):
        # same time but different room is fine
        diff_room = db_utils.check_time_room_conflict(self.now, "Z123")
        self.assertFalse(diff_room)

    def test_conflict_check_returns_exact_match_as_expected(self):
        exact_match = db_utils.check_time_room_conflict(self.now, self.loc)
        self.assertTrue(exact_match)

    def test_conflict_check_outside_lower_bound_default_time(self):
        time_11_16 = self.now + timedelta(minutes=16)
        # existing 11:00 event is more than 15 mins before new 11:16 event
        lower_check = db_utils.check_time_room_conflict(time_11_16, self.loc)
        self.assertFalse(lower_check)

    def test_conflict_check_inside_lower_bound_of_default(self):
        time_11_15 = self.now + timedelta(minutes=15)
        #existing 11:00 event is within 15 minutes before new 11:15 event
        edge_lower = db_utils.check_time_room_conflict(time_11_15, self.loc)
        self.assertTrue(edge_lower)

        time_11_10 = self.now + timedelta(minutes=10)
        inside_lower = db_utils.check_time_room_conflict(time_11_10, self.loc)
        self.assertTrue(inside_lower)

    def test_conflict_check_outside_upper_bound_default_time(self):
        time_10_29 = self.now - timedelta(minutes=31)
        # exisiting 11:00 event is more than 30 minutes after new 10:29 event
        upper_check = db_utils.check_time_room_conflict(time_10_29, self.loc)
        self.assertFalse(upper_check)

    def test_conflict_inside_upper_bound_default_time(self):
        time_10_30 = self.now - timedelta(minutes=30)
        # existing 11:00 event is within 30 minutes of new 10:30 event
        edge_upper = db_utils.check_time_room_conflict(time_10_30, self.loc)
        self.assertTrue(edge_upper)

        time_10_45 = self.now - timedelta(minutes=15)
        inside_upper = db_utils.check_time_room_conflict(time_10_45, self.loc)
        self.assertTrue(inside_upper)

    def test_conflict_inside_and_outside_non_default_upper_time(self):
        time_10_01 = self.now - timedelta(minutes=59)
        # existing 11:00 time is within 60 mins after new 10:01 event
        inside_upper = db_utils.check_time_room_conflict(time_10_01, 
                                                        self.loc, mins_after=60)
        self.assertTrue(inside_upper)

        time_9_50 = self.now - timedelta(minutes=70)
        outside_upper = db_utils.check_time_room_conflict(time_9_50, 
                                                        self.loc, mins_after=60)
        self.assertFalse(outside_upper)

    def test_conflict_inside_and_outside_non_default_lower_time(self):
        time_11_59 = self.now + timedelta(minutes=59)
        # existing 11:00 time is within 60 mins beforw new 11:59 event
        inside_lower = db_utils.check_time_room_conflict(time_11_59, 
                                                        self.loc, mins_before=60)
        self.assertTrue(inside_lower)

        time_12_01 = self.now - timedelta(minutes=61)
        outside_lower = db_utils.check_time_room_conflict(time_12_01, 
                                                        self.loc, mins_before=60)
        self.assertFalse(outside_lower)


class TestTweetUtils(TestCase):
    """Test that the Tweet utils funcs behave as expected in isolation"""

    def setUp(self):
        OutgoingConfig.objects.create(auto_send=True, 
                                    default_send_interval=1, 
                                    ignore_users=[12345,])

    def schedule_tweet_helper(self, talk_time):
        screen_name = "tw_testy"
        tweet = "a test tweet"
        tweet_id = 123456

        tweet_utils.schedule_tweets(screen_name, tweet, tweet_id, 
                                    talk_time, num_tweets=2)

    @freeze_time("2017-08-05")
    def test_schedule_tweets_saves_legit_tweets_to_db(self):
        tweets_in_db_before = OutgoingTweet.objects.all()
        self.assertEqual(len(tweets_in_db_before), 0)

        talk_time = datetime.now(timezone.utc)
        self.schedule_tweet_helper(talk_time)

        tweets_in_db_after = OutgoingTweet.objects.all()
        self.assertEqual(len(tweets_in_db_after), 2)

    @freeze_time("2017-08-05")
    def test_schedule_tweets_sets_approved_to_0_if_tweet_within_30_mins(self):
        """Test to check tweets within 30 mins not auto approved"""
        talk_time = datetime.now(timezone.utc) + timedelta(minutes=15)
        self.schedule_tweet_helper(talk_time)
        scheduled_tweet = OutgoingTweet.objects.first()

        # tweet should need to be approved if event time is within 30 mins
        self.assertEqual(scheduled_tweet.approved, 0)

    def test_schedule_tweets_sets_approved_to_1_if_tweet_outside_30_mins(self):
        talk_time = datetime.now(timezone.utc) + timedelta(minutes=31)
        self.schedule_tweet_helper(talk_time)
        scheduled_tweet = OutgoingTweet.objects.first()

        self.assertEqual(scheduled_tweet.approved, 1)

    def test_schedule_tweets_sets_approved_to_0_with_time_in_past(self):
        talk_time = datetime.now(timezone.utc) - timedelta(minutes=30)
        self.schedule_tweet_helper(talk_time)
        scheduled_tweet = OutgoingTweet.objects.first()

        self.assertEqual(scheduled_tweet.approved, 0)


class TestTweetUtilsRegex(TestCase):
    """Make sure the regex to extract room from a tweet behaves as expected"""

    def setUp(self):
        OutgoingConfig.objects.create(auto_send=True, 
                                    default_send_interval=1, 
                                    ignore_users=[12345,])
        # what SUTime returns when it parses time in tweet
        self.extracted_time = [
                                {
                                'type': 'TIME', 
                                'end': 24, 
                                'text': '2:05pm', 
                                'value': '2017-04-11T14:05', 
                                'start': 18
                                }
                              ]
        self.no_extracted_time = []

    def test_get_time_and_room_correctly_returns_time_room_obj(self):
        tweet = "a test tweet R123 2:05pm"
        result = tweet_utils.get_time_and_room(tweet, self.extracted_time)

        expected_output = {'room': ['r123'], 'date': ['2017-04-11T14:05']}
        self.assertEqual(result, expected_output)

    def test_get_time_and_room_with_period_after_room_number(self):
        tweet = "a test tweet with a period after room num r123. 2:05pm"
        result = tweet_utils.get_time_and_room(tweet, self.extracted_time)

        expected_output = {'room': ['r123'], 'date': ['2017-04-11T14:05']}
        self.assertEqual(result, expected_output)

    def test_get_time_and_room_with_only_room_present(self):
        tweet = "a test tweet with only a room number present R123"
        result = tweet_utils.get_time_and_room(tweet, self.no_extracted_time)

        expected_output = {'room': ['r123'], 'date': []}
        self.assertEqual(result, expected_output)

    def test_get_time_and_room_with_only_time_present(self):
        tweet = "a test tweet with only a time present 2:05pm"
        result = tweet_utils.get_time_and_room(tweet, self.extracted_time)

        expected_output = {'room': [], 'date': ['2017-04-11T14:05']}
        self.assertEqual(result, expected_output)

    def test_clean_times_pulls_years_out_correctly(self):
        time_input = ['2017', '2017-05-18T17:00']
        result = tweet_utils.clean_times(time_input)
        self.assertEqual(result, ['2017-05-18T17:00'])

    def test_clean_times_pulls_multiple_years_out_correctly(self):
        time_input = ['2017', '2015', '1203', '2017-05-18T17:00']
        result = tweet_utils.clean_times(time_input)
        self.assertEqual(result, ['2017-05-18T17:00'])

    def test_check_date_mention_works_with_example_tweet(self):
        tweet_with_date = "@fakeuser \t \n http://www.example.com #pyconopenspaces 5/19"
        result = tweet_utils.check_date_metnion(tweet_with_date)
        self.assertEqual(result, ["5/19"])

    def test_check_date_mention_mulitple_return_false(self):
        tweet_multi = "5/19 5/20 5/21 a bunch of dates should return false"
        result = tweet_utils.check_date_metnion(tweet_multi)
        self.assertFalse(result)

    def test_check_date_mention_wrong_dates_return_false(self):
        tweet_wrong = "4/21 a talk for last month"
        result = tweet_utils.check_date_metnion(tweet_wrong)
        self.assertFalse(result)


class TestTimeUtils(TestCase):
    """Tests of the time utils used in bot"""

    @freeze_time("2017-08-05")
    def test_convert_to_utc_returns_correct_time(self):
        time_str_from_sutime = "2017-04-11T08:00"
        converted_time = time_utils.convert_to_utc(time_str_from_sutime)

        utc = pytz.utc
        expected_output = datetime(2017, 8, 4, 15, tzinfo=utc) 

        self.assertEqual(converted_time, expected_output)

    @freeze_time("2017-08-05")
    def test_check_start_time_helper_func(self):
        talk_time = datetime.now(timezone.utc) + timedelta(minutes=15)
        within_30_mins = time_utils.check_start_time(talk_time)
        self.assertTrue(within_30_mins)

        talk_time = datetime.now(timezone.utc) + timedelta(minutes=31)
        outside_30_mins = time_utils.check_start_time(talk_time)
        self.assertFalse(outside_30_mins)

    @freeze_time("2017-08-05")
    def test_get_local_clock_time(self):
        clock_t = time_utils.get_local_clock_time()
        self.assertEqual(clock_t, "17:00")
