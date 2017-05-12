import datetime
import mock
import unittest

from streambot import Streambot

class TestStreambotMethods(unittest.TestCase):

    @mock.patch("streambot.Streambot.__init__")
    def setUp(self, fake_init):
        fake_init.return_value = None
        self.S_bot = Streambot()
        
    def test_value_check_zero_valid_values(self):
        time_room_obj = {
            "date": [],
            "room": []
        }
        output = self.S_bot.value_check(time_room_obj)
        self.assertEqual(output, (0, 0))

    def test_value_check_one_time_value(self):
        time_room_obj = {
            "date": [datetime.datetime.utcnow()],
            "room": []
        }
        output = self.S_bot.value_check(time_room_obj)
        self.assertEqual(output, (0, 1))

    def test_value_check_one_room_value(self):
        time_room_obj = {
            "date": [],
            "room": ["A123",]
        }
        output = self.S_bot.value_check(time_room_obj)
        self.assertEqual(output, (1, 0))

    def test_multiple_values_for_each(self):
        time_room_obj = {
            "date": [datetime.datetime.utcnow(), datetime.datetime.utcnow()],
            "room": ["A123", "B123"]
        }
        output = self.S_bot.value_check(time_room_obj)
        self.assertEqual(output, (2, 2))

    @mock.patch("openspaces.bot_utils.tweet_utils.schedule_tweets")
    @mock.patch("openspaces.bot_utils.db_utils.create_event")
    @mock.patch("streambot.Streambot.send_slack_message")
    @mock.patch("openspaces.bot_utils.db_utils.check_time_room_conflict")
    @mock.patch("openspaces.bot_utils.time_utils.convert_to_utc")
    @mock.patch("streambot.Streambot.parse_time_room")
    def test_retweet_logic_with_valid_time_and_room(self, t_r_parse, 
                                                    time_convert, conflict,
                                                    slack_message, create_event,
                                                    schedule_tweets):

        # fake values for info extracted from tweet and no event conflict
        t_r_parse.return_value = {
            "date": [datetime.datetime.utcnow()],
            "room": ["A123"]
        }
        conflict.return_value = False

        self.S_bot.retweet_logic("fake tweet", 12345, "screen_name", 12345)

        # these methods should be called once if tweet has exactly 1 room & 1 time
        self.assertEqual(t_r_parse.call_count, 1)
        self.assertEqual(time_convert.call_count, 1)
        self.assertEqual(conflict.call_count, 1)
        self.assertEqual(slack_message.call_count, 1)
        self.assertEqual(create_event.call_count, 1)
        self.assertEqual(schedule_tweets.call_count, 1)

    @mock.patch("streambot.Streambot.send_slack_message")
    @mock.patch("streambot.Streambot.parse_time_room")
    def test_retweet_logic_with_only_valid_room(self, t_r_parse, slack_message):

        # with only 1 room a single slack message should be sent
        t_r_parse.return_value = {
            "date": [],
            "room": ["A123"]
        }
        
        self.S_bot.retweet_logic("fake tweet", 12345, "screen_name", 12345)
        self.assertEqual(t_r_parse.call_count, 1)
        self.assertEqual(slack_message.call_count, 1)

    @mock.patch("streambot.Streambot.send_slack_message")
    @mock.patch("streambot.Streambot.parse_time_room")
    def test_retweet_logic_with_only_valid_time(self, t_r_parse, slack_message):

        # with only 1 time a single slack message should be sent
        t_r_parse.return_value = {
            "date": [datetime.datetime.utcnow()],
            "room": []
        }
        
        self.S_bot.retweet_logic("fake tweet", 12345, "screen_name", 12345)
        self.assertEqual(t_r_parse.call_count, 1)
        self.assertEqual(slack_message.call_count, 1)

    @mock.patch("streambot.Streambot.send_slack_message")
    @mock.patch("streambot.Streambot.parse_time_room")
    def test_retweet_logic_with_multiple_valid_rooms_times(self, t_r_parse, slack_message):

        # with mulitple times and rooms only a slack message should be sent
        t_r_parse.return_value = {
            "date": [datetime.datetime.utcnow(), datetime.datetime.utcnow()],
            "room": ["A123", "B123"]
        }
        
        self.S_bot.retweet_logic("fake tweet", 12345, "screen_name", 12345)
        self.assertEqual(t_r_parse.call_count, 1)
        self.assertEqual(slack_message.call_count, 1)

    @mock.patch("streambot.Streambot.parse_time_room")
    def test_retweet_logic_with_no_time_or_room(self, t_r_parse):

        # with no valid times or rooms nothing should be called
        t_r_parse.return_value = {
            "date": [],
            "room": []
        }

        self.S_bot.retweet_logic("fake tweet", 12345, "screen_name", 12345)
        self.assertEqual(t_r_parse.call_count, 1)
    

if __name__ == '__main__':
    unittest.main()