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



if __name__ == '__main__':
    unittest.main()