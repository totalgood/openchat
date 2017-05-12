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
        self.assertEqual(output, (0,0))




if __name__ == '__main__':
    unittest.main()